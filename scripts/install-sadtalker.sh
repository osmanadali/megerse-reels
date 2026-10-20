set -e
cd /home/user/tools
[ -d SadTalker ] || git clone -q --depth 1 https://github.com/OpenTalker/SadTalker.git
cd SadTalker
uv venv -q -p 3.10 .venv
. .venv/bin/activate
uv pip install -q torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu
uv pip install -q "setuptools<70" "numpy<1.24" face_alignment==1.3.5 imageio==2.19.3 imageio-ffmpeg==0.4.7 librosa==0.9.2 numba resampy==0.3.1 pydub==0.25.1 scipy==1.10.1 kornia==0.6.8 tqdm yacs==0.1.8 pyyaml joblib==1.1.0 scikit-image==0.19.3 basicsr==1.4.2 facexlib==0.3.0 gfpgan safetensors opencv-python-headless
# torchvision uyumluluk yaması (basicsr)
f=$(python -c "import basicsr,os;print(os.path.dirname(basicsr.__file__))")/data/degradations.py
sed -i 's/from torchvision.transforms.functional_tensor import/from torchvision.transforms.functional import/' $f
bash scripts/download_models.sh
echo KURULUM_TAMAM
