"""
main module to run GFPGAN gradio demo
"""
import os
import cv2
import gradio as gr
import torch
from basicsr.archs.srvgg_arch import SRVGGNetCompact
from gfpgan.utils import GFPGANer
from realesrgan.utils import RealESRGANer

os.system("pip freeze")
if not os.path.exists('realesr-general-x4v3.pth'):
    os.system("wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth -P .")
if not os.path.exists('GFPGANv1.2.pth'):
    os.system("wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.2.pth -P .")
if not os.path.exists('GFPGANv1.3.pth'):
    os.system("wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth -P .")
if not os.path.exists('GFPGANv1.4.pth'):
    os.system("wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth -P .")
if not os.path.exists('RestoreFormer.pth'):
    os.system("wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/RestoreFormer.pth -P .")
if not os.path.exists('CodeFormer.pth'):
    os.system("wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/CodeFormer.pth -P .")
torch.hub.download_url_to_file(
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Abraham_Lincoln_O-77_matte_collodion_print.jpg/1024px-Abraham_Lincoln_O-77_matte_collodion_print.jpg',
    'lincoln.jpg')
torch.hub.download_url_to_file(
    'https://user-images.githubusercontent.com/17445847/187400315-87a90ac9-d231-45d6-b377-38702bd1838f.jpg',
    'AI-generate.jpg')
torch.hub.download_url_to_file(
    'https://user-images.githubusercontent.com/17445847/187400981-8a58f7a4-ef61-42d9-af80-bc6234cef860.jpg',
    'Blake_Lively.jpg')
torch.hub.download_url_to_file(
    'https://user-images.githubusercontent.com/17445847/187401133-8a3bf269-5b4d-4432-b2f0-6d26ee1d3307.png',
    '10045.png')

model = SRVGGNetCompact(num_in_ch = 3, num_out_ch = 3, 
                        num_feat = 64, num_conv = 32, 
                        upscale = 4, act_type = 'prelu')
MODEL_PATH = 'realesr-general-x4v3.pth'
half = True if torch.cuda.is_available() else False
upsampler = RealESRGANer(scale = 4, model_path = MODEL_PATH, 
                         model = model, tile = 0, tile_pad = 10, 
                         pre_pad = 0, half = half)

os.makedirs('output', exist_ok=True)

def refine_image(img: bytes, version: str, scale: int)-> str:
    """
    refine_image method take a Pillow image and mode as input and after enhancing 
    the image resolution save it and return the image path and output image.

    Parameters
    ----------
    input_image: Image
        Pillow image input by te user.
    version: str
        version contain the version of the model.
    scale: int
        scale contain the nuemric value represents the scale.
    """
    if scale > 4:
        scale = 4
    try:
        extension = os.path.splitext(os.path.basename(str(img)))[1]
        img = cv2.imread(img, cv2.IMREAD_UNCHANGED)
        if len(img.shape) == 3 and img.shape[2] == 4:
            img_mode = 'RGBA'
        elif len(img.shape) == 2:
            img_mode = None
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_mode = None

        height, width = img.shape[0:2]
        if height > 3500 or width > 3500:
            print('too large size')
            return None, None     
        if height < 300:
            img = cv2.resize(img, (width * 2, height * 2),
                             interpolation = cv2.INTER_LANCZOS4)
        if version == 'v1.2':
            face_enhancer = GFPGANer(
            model_path = 'GFPGANv1.2.pth', upscale = 2,
            arch = 'clean', channel_multiplier = 2,
            bg_upsampler = upsampler)
        elif version == 'v1.3':
            face_enhancer = GFPGANer(
            model_path = 'GFPGANv1.3.pth', upscale = 2, arch = 'clean', 
            channel_multiplier = 2, bg_upsampler = upsampler)
        elif version == 'v1.4':
            face_enhancer = GFPGANer(
            model_path='GFPGANv1.4.pth', upscale = 2, 
            arch = 'clean', channel_multiplier = 2, 
            bg_upsampler = upsampler)
        elif version == 'RestoreFormer':
            face_enhancer = GFPGANer(
            model_path = 'RestoreFormer.pth', upscale = 2, 
            arch = 'RestoreFormer', channel_multiplier = 2, 
            bg_upsampler = upsampler)
        try:
            _, _, output = face_enhancer.enhance(img, has_aligned = False, 
                                                 only_center_face = False, 
                                                 paste_back = True)
        except RuntimeError as error:
            print('Error', error)

        try:
            if scale != 2:
                interpolation = cv2.INTER_AREA if scale < 2 else cv2.INTER_LANCZOS4
                img_height, img_width = img.shape[0:2]
                output = cv2.resize(output, (int(img_width * scale / 2),
                                             int(img_height * scale / 2)),
                                             interpolation = interpolation)
        except Exception as error:
            print('wrong scale input.', error)
        if img_mode == 'RGBA':
            extension = 'png'
        else:
            extension = 'jpg'
        save_path = f'output/out.{extension}'
        cv2.imwrite(save_path, output)

        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output, save_path
    except Exception as error:
        print('global exception', error)
        return None, None


title = "GFPGAN Face Restoration"
demo = gr.Interface(
    refine_image, [
        gr.Image(type="filepath", label="Input"),
        gr.Radio(['v1.2', 'v1.3', 'v1.4', 'RestoreFormer'], 
                 type = "value", value = 'v1.4', label = 'version'),
        gr.Number(label="Rescaling factor", value=2),
    ], [
        gr.Image(type="numpy", label="Output (The whole image)"),
        gr.File(label="Download the output image")
    ],
    title=title,
    examples=[['AI-generate.jpg', 'v1.4', 2],
              ['lincoln.jpg', 'v1.4', 2],
              ['Blake_Lively.jpg', 'v1.4', 2],
              ['10045.png', 'v1.4', 2]])
demo.queue().launch(debug = True, share = True)
