"""V7.4 SOTA Killer - Model Architecture Definition (extracted from notebook)"""
import io, math, random
from dataclasses import dataclass, asdict
import torch, torch.nn as nn, torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from torchvision.transforms import functional as TF
from torchvision.models import VGG19_Weights, vgg19

NST_LAYERS = {'0':'conv_1','5':'conv_2','10':'conv_3','19':'conv_4','28':'conv_5'}

def extract_features(model, image):
    feats = {}; x = image
    for name, layer in model._modules.items():
        x = layer(x)
        if name in NST_LAYERS: feats[NST_LAYERS[name]] = x
    return feats

def sobel_edges(x):
    gray = x.mean(dim=1, keepdim=True)
    kx = torch.tensor([[1,0,-1],[2,0,-2],[1,0,-1]], dtype=x.dtype, device=x.device).view(1,1,3,3)
    ky = torch.tensor([[1,2,1],[0,0,0],[-1,-2,-1]], dtype=x.dtype, device=x.device).view(1,1,3,3)
    return torch.cat([F.conv2d(gray,kx,padding=1), F.conv2d(gray,ky,padding=1)], dim=1)

def haar_dwt2(x):
    if x.shape[-2]%2==1: x=x[...,:-1,:]
    if x.shape[-1]%2==1: x=x[...,:,:-1]
    x00,x01,x10,x11 = x[...,0::2,0::2],x[...,0::2,1::2],x[...,1::2,0::2],x[...,1::2,1::2]
    return 0.5*(x00+x01+x10+x11),0.5*(x00-x01+x10-x11),0.5*(x00+x01-x10-x11),0.5*(x00-x01-x10+x11)

def texture_attention(x):
    edges = sobel_edges(x).abs().mean(dim=1, keepdim=True)
    _,lh,hl,hh = haar_dwt2(x)
    freq = (lh.abs().mean(1,True)+hl.abs().mean(1,True)+hh.abs().mean(1,True))/3.0
    freq = F.interpolate(freq, size=x.shape[-2:], mode='bilinear', align_corners=False)
    attn = edges + 0.5*freq
    attn = attn/(attn.amax(dim=(-2,-1),keepdim=True)+1e-6)
    return attn.clamp(0.0,1.0)

def group_norm_groups(c):
    for g in [16,8,4,2]:
        if c%g==0: return g
    return 1

@dataclass
class ModelConfig:
    image_channels:int=3; hidden_channels:int=128; token_channels:int=64; token_size:int=32
    residual_scale:float=0.025; reverse_refine_scale:float=0.22
    reverse_margin:float=0.03; style_margin:float=0.01
    mask_texture_floor:float=0.60; eval_strength:float=1.24
    train_strength_min:float=1.02; train_strength_max:float=1.30
    serial_prior_blend:float=0.3

class ConvBlock(nn.Module):
    def __init__(self, inc, outc, stride=1):
        super().__init__()
        self.block = nn.Sequential(nn.Conv2d(inc,outc,3,stride=stride,padding=1), nn.GroupNorm(group_norm_groups(outc),outc), nn.GELU())
    def forward(self,x): return self.block(x)

class ResidualBlock(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.body = nn.Sequential(nn.Conv2d(c,c,3,padding=1), nn.GroupNorm(group_norm_groups(c),c), nn.GELU(), nn.Conv2d(c,c,3,padding=1), nn.GroupNorm(group_norm_groups(c),c))
    def forward(self,x): return F.gelu(x+self.body(x))

class HybridTokenizer(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.cfg=cfg
        self.cnn_encoder = nn.Sequential(ConvBlock(3,64,stride=2),ConvBlock(64,128,stride=2),ConvBlock(128,128,stride=2),ResidualBlock(128),ResidualBlock(128),nn.Conv2d(128,64,1))
        self.vgg_proj = nn.Sequential(nn.Conv2d(256,128,1),nn.GELU(),nn.Conv2d(128,64,1))
        self.thumb_refine = nn.Sequential(ConvBlock(3,64),ResidualBlock(64),nn.Conv2d(64,3,1),nn.Sigmoid())
    def forward(self, content, vgg_model):
        cnn_token = F.adaptive_avg_pool2d(self.cnn_encoder(content),(32,32))
        with torch.no_grad(): vgg_feat = extract_features(vgg_model, content)['conv_3']
        vgg_token = F.adaptive_avg_pool2d(self.vgg_proj(vgg_feat),(32,32))
        token = torch.tanh(cnn_token+vgg_token)
        raw_thumb = F.interpolate(content,size=(32,32),mode='bilinear',align_corners=False)
        thumb = self.thumb_refine(raw_thumb)
        return {'token':token,'thumbnail':thumb}

class StegoEncoder(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.cfg=cfg
        fused = 3+64+3+2+3  # cover+token+thumb+edges+diff = 75
        self.stem = nn.Sequential(ConvBlock(fused,128),ResidualBlock(128),ResidualBlock(128),ResidualBlock(128))
        self.res_head = nn.Conv2d(128,3,3,padding=1)
        self.mask_head = nn.Conv2d(128,3,3,padding=1)
    def forward(self, cover, token, thumb, strength=1.0):
        token_up = F.interpolate(token,size=cover.shape[-2:],mode='bilinear',align_corners=False)
        thumb_up = F.interpolate(thumb,size=cover.shape[-2:],mode='bilinear',align_corners=False)
        edges = sobel_edges(cover); diff = cover-thumb_up
        feat = self.stem(torch.cat([cover,token_up,thumb_up,edges,diff],dim=1))
        residual = torch.tanh(self.res_head(feat))
        mask = torch.sigmoid(self.mask_head(feat)) * (self.cfg.mask_texture_floor+(1-self.cfg.mask_texture_floor)*texture_attention(cover).detach())
        return torch.clamp(cover+(self.cfg.residual_scale*float(strength))*mask*residual,0.,1.), residual

class StegoDecoder(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.cfg=cfg
        self.stem = nn.Sequential(ConvBlock(3,64,stride=2),ConvBlock(64,128,stride=2),ConvBlock(128,128,stride=2),ResidualBlock(128),ResidualBlock(128))
        self.token_head = nn.Conv2d(128,64,1)
        self.thumb_head = nn.Sequential(nn.Conv2d(128,3,1),nn.Sigmoid())
    def forward(self, image):
        feat = F.adaptive_avg_pool2d(self.stem(image),(32,32))
        return {'token':self.token_head(feat),'thumbnail':self.thumb_head(feat)}

class TokenPriorDecoder(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.seed = nn.Sequential(ConvBlock(67,128),ResidualBlock(128),ResidualBlock(128))
        self.up64 = nn.Sequential(ConvBlock(128,128),ResidualBlock(128))
        self.up128 = nn.Sequential(ConvBlock(128,128),ResidualBlock(128))
        self.up256 = nn.Sequential(ConvBlock(128,64),ResidualBlock(64))
        self.out = nn.Sequential(nn.Conv2d(64,3,3,padding=1),nn.Sigmoid())
    def forward(self, token, thumb):
        x32 = self.seed(torch.cat([token,thumb],dim=1))
        x64 = self.up64(F.interpolate(x32,scale_factor=2,mode='bilinear',align_corners=False))
        x128 = self.up128(F.interpolate(x64,scale_factor=2,mode='bilinear',align_corners=False))
        x256 = self.up256(F.interpolate(x128,scale_factor=2,mode='bilinear',align_corners=False))
        return self.out(x256), {'x128':x128,'x256':x256}

class ReverseDecoder(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.cfg=cfg
        self.prior_decoder = TokenPriorDecoder(cfg)
        inc = 3+3+3+64+2+2+3  # 80
        self.enc0 = nn.Sequential(ConvBlock(inc,128),ResidualBlock(128))
        self.down1 = nn.Sequential(ConvBlock(128,128,stride=2),ResidualBlock(128))
        self.down2 = nn.Sequential(ConvBlock(128,256,stride=2),ResidualBlock(256))
        self.bottleneck = nn.Sequential(ResidualBlock(256),ResidualBlock(256))
        self.up1 = nn.Sequential(ConvBlock(512,128),ResidualBlock(128))
        self.up2 = nn.Sequential(ConvBlock(320,128),ResidualBlock(128))
        self.blend_head = nn.Conv2d(128,1,3,padding=1)
        self.delta_head = nn.Conv2d(128,3,3,padding=1)
    def forward(self, stego, token, thumb):
        prior, pf = self.prior_decoder(token,thumb)
        thu = F.interpolate(thumb,size=stego.shape[-2:],mode='bilinear',align_corners=False)
        tku = F.interpolate(token,size=stego.shape[-2:],mode='bilinear',align_corners=False)
        x = torch.cat([stego,prior,thu,tku,sobel_edges(stego),sobel_edges(prior),torch.abs(stego-prior)],dim=1)
        e0=self.enc0(x); e1=self.down1(e0); e2=self.down2(e1); b=self.bottleneck(e2)
        u1=self.up1(torch.cat([F.interpolate(b,size=e1.shape[-2:],mode='bilinear',align_corners=False),e1,pf['x128']],1))
        u2=self.up2(torch.cat([F.interpolate(u1,size=e0.shape[-2:],mode='bilinear',align_corners=False),e0,pf['x256']],1))
        blend=torch.sigmoid(self.blend_head(u2)); delta=torch.tanh(self.delta_head(u2))
        return {'prior':prior,'image':torch.clamp(blend*prior+(1-blend)*thu+self.cfg.reverse_refine_scale*delta,0.,1.)}

class BenchmarkSystemV7(nn.Module):
    def __init__(self, cfg):
        super().__init__(); self.cfg=cfg
        self.tokenizer=HybridTokenizer(cfg); self.encoder=StegoEncoder(cfg)
        self.decoder=StegoDecoder(cfg); self.reverse_decoder=ReverseDecoder(cfg)
