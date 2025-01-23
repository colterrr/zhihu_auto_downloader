import mitmproxy.http
import os
import requests
import json
import re

download_dir = "download"

def download_image(url, save_path):
    """
    从指定url下载图片并保存到本地
    """
    if url.startswith("data:image/"):
        # 如果链接以 "data:" 开头，则直接写入数据到文件
        with open(save_path, "wb") as f:
            f.write(url.split(",", 1)[1].encode("utf-8"))
    else:
        response = requests.get(url)
        with open(save_path, "wb") as f:
            f.write(response.content)

def handle_mark(text, marks):
    """
    给文本和mark列表,返回处理后的markdown文本字符串
    """
    result = []
    last_end = 0
    for mark in marks:
        start = mark["start_index"]
        end = mark["end_index"]
        result.append(text[last_end:start]) #加入当前mark前的文本内容
        if mark["type"] == "bold":
            result.append(f"**{text[start:end]}**")
            last_end = end
        elif mark["type"] == "formula":
            result.append('$' + mark["formula"]["content"] + '$')
            last_end = end
        elif mark["type"] == "link":
            result.append(f"[{text[start:end]}]({mark["link"]["href"]})")
            last_end = end
    result.append(text[last_end:] + '\n\n') #加入无mark的末尾部分
    return ''.join(result)

def response2md(json_dict):
    author = json_dict['author']['fullname']
    time = json_dict['content_end_info']['create_time_text'][:10]
    question = json_dict["header"]["text"]
    markdown = f"# {question}\n\n**Author**:{author}\n\n"
    markdown_name = time + '_' + question + '_' + author
    # 替换非法字符为空字符串
    markdown_name = re.sub(r'[\/:*?"<>|]', '', markdown_name)

    if os.path.exists(f"{download_dir}/{markdown_name}.md") or os.path.exists(f"{download_dir}/{markdown_name}"):
        # 存在相同文件，不重复保存
        return
    
    image_index = 0 #图片索引，用来记录文章里含有几张图片
    extensions = ['.jpg', '.png', '.gif'] #图片可能的格式后缀
    for segment in json_dict["structured_content"]["segments"]:
        if segment["type"] == "paragraph":
            markdown += handle_mark(segment["paragraph"]["text"], segment["paragraph"]["marks"])

        elif segment["type"] == "list_node":
            items = segment["list_node"]["items"]
            for i in range(len(items)):
                markdown += f"{i+1}. "
                markdown += handle_mark(items[i]["text"], items[i]["marks"])
        elif segment["type"] == "heading":
            markdown += f"{"#" * segment["heading"]["level"]} {segment["heading"]["text"]}\n\n" 

        elif segment["type"] == "image":
            image_index += 1            
            url = segment["image"]["urls"][0]
            #查找图片格式后缀并添加至文件名
            for ext in  extensions:
                if url.find(ext) != -1:
                    img_name = f"img{image_index}{ext}"
                    break

            img_dir_path = f"{download_dir}/{markdown_name}"
            img_path = img_dir_path + '/' + img_name
            if not os.path.exists(img_dir_path):
                os.makedirs(img_dir_path)
            download_image(url, img_path)

            markdown += f"![]({img_name})\n\n"
    
    if image_index > 0: 
        #若有图片则md保存到相关子目录
        markdown_savepath = f"{download_dir}/{markdown_name}"   
    else:
        markdown_savepath = download_dir
    with open(f"{markdown_savepath}/{markdown_name}.md", 'w', encoding='utf-8') as md:
        md.write(markdown)

def response(flow: mitmproxy.http.HTTPFlow):
    if "api.zhihu.com" in flow.request.host and ("/answers/" in flow.request.path or "/articles/" in flow.request.path or "/pins/" in flow.request.path):
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        response_content = flow.response.content
        response_text = response_content.decode('utf-8' )
        data = json.loads(response_text)
        response2md(data)