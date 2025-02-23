## 视图函数
from django.shortcuts import render, redirect
from photo.models import Photo
from django.contrib.auth import authenticate, login, logout

from django.core.paginator import Paginator


import oss2

# 填入阿里云账号的 <AccessKey ID> 和 <AccessKey Secret>
# auth   = oss2.Auth('<AccessKey ID>', '<AccessKey Secret>')
# 填入 OSS 的 <域名> 和 <Bucket名>
# bucket = oss2.Bucket(auth, '<oss域名>', '<Bucket名>')

class ObjIterator(oss2.ObjectIteratorV2):
    # 初始化时立即抓取图片数据
    def __init__(self, bucket):
        super().__init__(bucket)    ## super()是内嵌函数，用于调用父类方法
        self.fetch_with_retry()     ## 在网络请求失败时自动重试

    # 分页要求实现__len__
    def __len__(self):              ## 返回当前迭代器中对象数量
        return len(self.entries)    ## entries()方法获取所有对象信息并返回一个列表

    # 分页要求实现__getitem__
    def __getitem__(self, key):   ##根据文件名获取文件信息  
        return self.entries[key]## key指当前文件的文件名

    # 修改图片排序方式
    def _fetch(self):## list_objects_v2()方法获取对象列表
        result = self.bucket.list_objects_v2(prefix=self.prefix,      ## prefix属性获取当前对象前缀或文件名
                                          delimiter=self.delimiter,   ## 表示当前迭代器针对的分隔符，用于区分目录和文件
                                          continuation_token=self.next_marker,##下一个分页的marker,用于继续遍历对象列表
                                          start_after=self.start_after,## 指定迭代器开始位置
                                          fetch_owner=self.fetch_owner,
                                          encoding_type=self.encoding_type,
                                          max_keys=self.max_keys,
                                          headers=self.headers)
        self.entries = result.object_list + [oss2.models.SimplifiedObjectInfo(prefix, None, None, None, None, None)
                                             for prefix in result.prefix_list]
        # 让图片以上传时间倒序
        self.entries.sort(key=lambda obj: -obj.last_modified)

        return result.is_truncated, result.next_continuation_token  ## is_truncated表示当前分页是否被截断，即是否存在更多的对象等待获取

def oss_home(request):
    raise ValueError("""
请确保 /photo/views.py 中有关阿里云的信息填写正确。
(即 auth 和 bucket 属性中的信息)。
完成后将它们取消注释，并删除此行raise代码。""")

    photos       = ObjIterator(bucket)
    paginator    = Paginator(photos, 6)
    page_number  = request.GET.get('page')
    paged_photos = paginator.get_page(page_number)
    context      = {'photos': paged_photos}


    # 省略登入登出的POST请求代码
    # ...

    return render(request, 'photo/oss_list.html', context)



def home(request):
    photos = Photo.objects.all()
    paginator    = Paginator(photos, 5)
    page_number  = request.GET.get('page')
    paged_photos = paginator.get_page(page_number)
    context = {'photos': paged_photos}

    # 处理登入登出的POST请求
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)
        # 登入
        if user is not None and user.is_superuser:
            login(request, user)
        # 登出
        isLogout  = request.POST.get('isLogout')
        if isLogout == 'True':
            logout(request)
    return render(request, 'photo/list.html', context)


def upload(request):
    if request.method == 'POST' and request.user.is_superuser:
        images = request.FILES.getlist('images')
        for i in images:
            photo = Photo(image=i)
            photo.save()
    return redirect('home')





from django.http import JsonResponse

# 无限滚动
def fetch_photos(request):
    photos       = Photo.objects.values()
    paginator    = Paginator(photos, 4)
    page_number  = int(request.GET.get('page'))
    data         = {}

    # 页码正确才返回数据
    if page_number <= paginator.num_pages:
        paged_photos = paginator.get_page(page_number)
        data.update({'photos': list(paged_photos)})

    return JsonResponse(data)