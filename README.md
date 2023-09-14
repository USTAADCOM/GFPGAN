# GFPGAN
GFP-GAN is a generative adversarial network for blind face restoration that leverages a generative facial prior (GFP). This Generative Facial Prior (GFP) is incorporated into the face restoration process via channel-split spatial feature transform layers, which allow for a good balance between realness and fidelity.

## Setup
  ```code
  conda create -n <env_name>
  conda activate <env_name>
  git clone https://github.com/USTAADCOM/GFPGAN.git
  cd GFPGAN
  pip install -r requirements.txt -q
  ```
## Project Structure
```bash
GFPGAN
  │ app.py
  │ README.md
  │ requirements.txt

```
## Run Gradio Demo
```code
python3 app.py 
```