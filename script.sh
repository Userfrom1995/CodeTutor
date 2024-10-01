docker run -it \
  -v ./volume:/home/dockeruser/code_files \
  --name code_runner \
  user1995/multi-lang-container-alpine
requirements.txt
docker run -u root -p 5001:5001 -it -v volume:/home/dockeruser/code_files --name code_runner user1995/multi-lang-container-alpine 