import sys
import os
sys.path.append('PlotNeuralNet')
from pycore.tikzeng import *
from pycore.blocks  import *

arch = [ 
    to_head('..'), 
    to_cor(),
    to_begin(),

    # =========================================================================
    # PART 1: TOKENIZER (Top)
    # =========================================================================
    
    # Secret Image C
    to_Conv("secret_C", s_filer=256, n_filer=3, offset="(0,0,0)", to="(0,0,0)", width=2, height=40, depth=40, caption="Secret C" ),
    
    # CNN Branch (Top part of Tokenizer)
    to_ConvConvRelu( name="tok_cnn1", s_filer=128, n_filer=(64,64), offset="(2,3,0)", to="(secret_C-east)", width=(3,3), height=30, depth=30, caption="CNN Branch" ),
    to_connection("secret_C", "tok_cnn1"),
    to_Pool("tok_pool1", offset="(0,0,0)", to="(tok_cnn1-east)", width=1, height=20, depth=20, opacity=0.5),
    to_ConvRes("tok_res1", s_filer=64, n_filer=128, offset="(1,0,0)", to="(tok_pool1-east)", width=4, height=20, depth=20, opacity=0.5, caption="ResBlocks"),
    to_Conv("tok_cnn2", s_filer=32, n_filer=64, offset="(1,0,0)", to="(tok_res1-east)", width=3, height=12, depth=12, caption="proj" ),

    # VGG Branch (Bottom part of Tokenizer)
    to_Conv("tok_vgg", s_filer=128, n_filer=256, offset="(2,-3,0)", to="(secret_C-east)", width=6, height=30, depth=30, caption="VGG conv_3" ),
    to_connection("secret_C", "tok_vgg"),
    to_Conv("tok_vgg_proj", s_filer=32, n_filer=64, offset="(2,0,0)", to="(tok_vgg-east)", width=3, height=12, depth=12, caption="proj" ),
    to_connection("tok_vgg", "tok_vgg_proj"),

    # Token and Thumbnail
    to_Sum("tok_sum", offset="(1,0,0)", to="(tok_cnn2-east)", radius=2.0, opacity=0.6),
    to_connection("tok_cnn2", "tok_sum"),
    to_connection("tok_vgg_proj", "tok_sum"),
    
    to_Conv("token_z", s_filer=32, n_filer=64, offset="(1,0,0)", to="(tok_sum-east)", width=3, height=12, depth=12, caption="Token z" ),
    to_connection("tok_sum", "token_z"),

    to_Conv("thumb_T", s_filer=32, n_filer=3, offset="(0,-2.5,0)", to="(token_z-south)", width=1, height=12, depth=12, caption="Thumb T" ),
    to_connection("tok_vgg_proj", "thumb_T"),

    # =========================================================================
    # PART 2: STEGO ENCODER (Middle)
    # =========================================================================
    
    # Cover Image
    to_Conv("cover_X", s_filer=256, n_filer=3, offset="(0,-12,0)", to="(secret_C-south)", width=2, height=40, depth=40, caption="Cover X" ),
    
    # Concat features
    to_Conv("concat_features", s_filer=256, n_filer=75, offset="(3,0,0)", to="(cover_X-east)", width=4, height=40, depth=40, caption="Concat" ),
    to_connection("cover_X", "concat_features"),
    to_connection("token_z", "concat_features"),
    to_connection("thumb_T", "concat_features"),

    # Encoder Trunk
    to_Conv("enc_stem", s_filer=256, n_filer=128, offset="(1.5,0,0)", to="(concat_features-east)", width=5, height=40, depth=40, caption="Stem" ),
    to_connection("concat_features", "enc_stem"),
    to_ConvRes("enc_res", s_filer=256, n_filer=128, offset="(2,0,0)", to="(enc_stem-east)", width=6, height=40, depth=40, opacity=0.8, caption="3x ResBlocks" ),
    to_connection("enc_stem", "enc_res"),

    # Heads (Residual and Mask)
    to_Conv("enc_res_head", s_filer=256, n_filer=3, offset="(3,2,0)", to="(enc_res-east)", width=2, height=40, depth=40, caption="Residual" ),
    to_connection("enc_res", "enc_res_head"),
    
    to_Conv("enc_mask_head", s_filer=256, n_filer=3, offset="(3,-2,0)", to="(enc_res-east)", width=2, height=40, depth=40, caption="Mask" ),
    to_connection("enc_res", "enc_mask_head"),

    # Multiplication and Addition
    to_Sum("enc_mult", offset="(2,-2,0)", to="(enc_res_head-east)", radius=2.0, opacity=0.6),
    to_connection("enc_res_head", "enc_mult"),
    to_connection("enc_mask_head", "enc_mult"),

    to_Sum("enc_add", offset="(2,0,0)", to="(enc_mult-east)", radius=2.0, opacity=0.6),
    to_connection("enc_mult", "enc_add"),
    to_skip(of="cover_X", to="enc_add", pos=7),

    to_Conv("stego_X", s_filer=256, n_filer=3, offset="(2,0,0)", to="(enc_add-east)", width=2, height=40, depth=40, caption="Stego X" ),
    to_connection("enc_add", "stego_X"),


    # =========================================================================
    # PART 3: REVERSE DECODER (Bottom)
    # =========================================================================
    
    # Decoder starts from Stego Image (or a copy of it)
    to_Conv("dec_stego", s_filer=256, n_filer=3, offset="(0,-12,0)", to="(cover_X-south)", width=2, height=40, depth=40, caption="Stego X" ),
    to_connection("stego_X", "dec_stego"),

    # Token Prior Decoder
    to_Conv("dec_prior_in", s_filer=32, n_filer=67, offset="(2,4,0)", to="(dec_stego-east)", width=3, height=12, depth=12, caption="z, T" ),
    to_ConvRes("dec_prior_up", s_filer=256, n_filer=64, offset="(2,0,0)", to="(dec_prior_in-east)", width=4, height=40, depth=40, opacity=0.8, caption="Prior Decoder" ),
    to_connection("dec_prior_in", "dec_prior_up"),

    # U-Net Refinement
    to_Conv("dec_unet_in", s_filer=256, n_filer=80, offset="(2,-4,0)", to="(dec_prior_up-east)", width=4, height=40, depth=40, caption="U-Net In" ),
    to_connection("dec_stego", "dec_unet_in"),
    to_connection("dec_prior_up", "dec_unet_in"),
    
    to_Pool("dec_pool", offset="(1,0,0)", to="(dec_unet_in-east)", width=1, height=20, depth=20, opacity=0.5),
    to_Conv("dec_bot", s_filer=64, n_filer=128, offset="(1,0,0)", to="(dec_pool-east)", width=6, height=10, depth=10, caption="Bottleneck" ),
    to_connection("dec_pool", "dec_bot"),
    to_Unpool("dec_unpool", offset="(1,0,0)", to="(dec_bot-east)", width=1, height=20, depth=20, opacity=0.5),
    to_connection("dec_bot", "dec_unpool"),
    to_Conv("dec_unet_out", s_filer=256, n_filer=64, offset="(1,0,0)", to="(dec_unpool-east)", width=4, height=40, depth=40, caption="U-Net Out" ),
    to_connection("dec_unpool", "dec_unet_out"),
    to_skip(of="dec_unet_in", to="dec_unet_out", pos=1.5),

    # Final Output
    to_Conv("content_C_hat", s_filer=256, n_filer=3, offset="(2,0,0)", to="(dec_unet_out-east)", width=2, height=40, depth=40, caption="Content C hat" ),
    to_connection("dec_unet_out", "content_C_hat"),

    to_end() 
]

def main():
    namefile = "fgss_architecture"
    to_generate(arch, namefile + '.tex' )

if __name__ == '__main__':
    main()
