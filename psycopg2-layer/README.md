How to build lambda layer with psycopg2-layer

mkdir psycopg2-layer
cd psycopg2-layer
mkdir -p python

above commands already done

enough to be inside psycopg2-layer

docker run --rm -v "%cd%/python:/python" public.ecr.aws/sam/build-python3.11 pip install psycopg2-binary -t /python

zip python directory with name psycopg2-layer.zip

W AWS Console:

IMPORTANT TO SET CORRECT REGION

Go to Lambda → Layers

Click “Create layer”

Name: psycopg2-layer

Upload: psycopg2-layer.zip

Compatible runtimes: ✅ Python 3.11

Click Create

Copy Layer ARN

Use ARN inside lamba definition in layer property



