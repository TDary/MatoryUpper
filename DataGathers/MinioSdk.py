import minio
import traceback

# minio服务封装函数
class Minio_SDK():
    def __init__(self,url:str,bucketName:str,access_key:str,secret_key:str) -> object:
        try:
            self.bucket = bucketName
            self.minio_client = None
            minioclient = minio.Minio(endpoint=url,access_key=access_key,secret_key=secret_key,secure=False)
            self.minio_client = minioclient
            return minioclient
        except:
            traceback.print_exception()
            return None
        
    # 上传一个元素
    def UploadItem(self,objName:str,filePath:str,contentType:str):
        try:
            if self.minio_client.bucket_exists(bucket_name=self.bucket):  # bucket_exists：检查桶是否存在
                pass
            else:
                self.minio_client.make_bucket(self.bucket)
                print(f"存储桶{self.bucket}创建成功")
                    # 上传调用
            self.minio_client.fput_object(bucket_name=self.bucket,object_name=objName,file_path=filePath,content_type=contentType)
            print(f"上传{filePath}到服务器成功")
        except:
            traceback.print_exception()
    
    # 下载一个元素
    def DownLoadItem(self,objName:str,filePath:str,contentType:str):
        try:
            if self.minio_client.bucket_exists(bucket_name=self.bucket):  # bucket_exists：检查桶是否存在
                pass
            else:
                raise Exception("f存储桶{self.bucket}不存在，请检查~")
            # 下载元素对象调用
            self.minio_client.fget_object(bucket_name=self.bucket,object_name=objName,file_path=filePath,content_type=contentType)
            print(f"下载{filePath}到本地成功")
        except:
            traceback.print_exception()


