import os
from dotenv import load_dotenv
from huggingface_hub import HfApi, upload_folder, upload_file


class HuggingFaceUploader:
    def __init__(self, username: str, token: str = None):
        load_dotenv()
        self.username = username
        self.token = token or os.getenv("HF_TOKEN")
        if not self.token:
            raise ValueError("HF_TOKEN not found in .env or passed explicitly.")
        self.api = HfApi(token=self.token)

    def create_repo(self, model_name: str, private: bool = True):
        repo_id = f"{self.username}/{model_name}"
        if not self.api.repo_exists(repo_id, repo_type="model"):
            self.api.create_repo(repo_id=repo_id, private=private)
            print(f"✅ Created repo: {repo_id}")
        else:
            print(f"ℹ️ Repo already exists: {repo_id}")
        return repo_id

    def upload_folder(self, model_name: str, local_folder: str, commit_message: str = "Initial model upload",
                      private: bool = True):
        repo_id = self.create_repo(model_name, private)
        upload_folder(
            repo_id=repo_id,
            folder_path=local_folder,
            path_in_repo="",
            commit_message=commit_message,
            token=self.token
        )
        print(f"📤 Uploaded folder '{local_folder}' to '{repo_id}'")

    def upload_file(self, model_name: str, file_path: str, path_in_repo: str = "", commit_message: str = "Update file",
                    private: bool = True):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"❌ File not found: {file_path}")
        repo_id = self.create_repo(model_name, private)
        upload_file(
            repo_id=repo_id,
            path_or_fileobj=file_path,
            path_in_repo=path_in_repo or os.path.basename(file_path),
            commit_message=commit_message,
            token=self.token
        )
        print(f"📤 Uploaded file '{file_path}' to '{repo_id}/{path_in_repo or os.path.basename(file_path)}'")
