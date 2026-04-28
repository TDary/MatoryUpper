import minio
import traceback

# minio服务封装函数
class Minio_SDK():
    def __init__(self, url: str, bucketName: str, access_key: str, secret_key: str):
        self.minio_client = None
        self.bucket = bucketName
        self._bucket_exists = False
        try:
            self.minio_client = minio.Minio(endpoint=url, access_key=access_key, secret_key=secret_key, secure=False)
            self._bucket_exists = self.minio_client.bucket_exists(bucket_name=self.bucket)
            if not self._bucket_exists:
                self.minio_client.make_bucket(self.bucket)
                print(f"存储桶{self.bucket}创建成功")
            print("Minio SDK连接成功")
        except:
            traceback.print_exc()

    def _ensure_bucket(self):
        """确保 bucket 存在，使用缓存结果避免重复网络请求"""
        if self._bucket_exists:
            return
        self._bucket_exists = self.minio_client.bucket_exists(bucket_name=self.bucket)
        if not self._bucket_exists:
            self.minio_client.make_bucket(self.bucket)
            print(f"存储桶{self.bucket}创建成功")

    # 上传一个元素
    def UploadItem(self, objName: str, filePath: str, contentType: str):
        try:
            self._ensure_bucket()
            self.minio_client.fput_object(bucket_name=self.bucket, object_name=objName, file_path=filePath, content_type=contentType)
            print(f"上传{filePath}到服务器成功")
        except:
            traceback.print_exc()

    # 下载一个元素
    def DownLoadItem(self, objName: str, filePath: str, contentType: str):
        try:
            self._ensure_bucket()
            self.minio_client.fget_object(bucket_name=self.bucket, object_name=objName, file_path=filePath, content_type=contentType)
            print(f"下载{filePath}到本地成功")
        except:
            traceback.print_exc()
