import mitmproxy.http
import os
import requests
import json
import re
from typing import Literal

text_type_ = Literal["answer", "article", "pin"]

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
    给文本和mark列表,返回处理后的markdown文本字符串 (结尾含两个换行符)
    """
    mark_insert = []
    for mark in marks:
        start = mark["start_index"]
        end = mark["end_index"]        
        if mark["type"] == "bold":
            mark_insert.append(("insert", start, "**"))
            mark_insert.append(("insert", end, "**"))
        elif mark["type"] == "formula":
            #formula_str = re.sub(r' ', '', mark["formula"]["content"])
            # 去除可能的书写不规范的formula首尾位置的空格
            formula_str = mark["formula"]["content"]
            if formula_str[0] == ' ':
                formula_str = formula_str[1:]
            if formula_str[-1] == ' ':
                formula_str = formula_str[:-1]
            mark_insert.append(("replace", start, end, '$' + formula_str + '$'))
        elif mark["type"] == "link":
            mark_insert.append(("insert", start, "["))
            mark_insert.append(("insert", end, f"]({mark["link"]["href"]})"))
    mark_insert.sort(key=lambda x: x[1])

    result = []
    last_end = 0
    for mark in mark_insert:
        if mark[0] == "insert":
            result.append(text[last_end:mark[1]] + mark[2])
            if last_end < mark[1]:
                last_end = mark[1]
        elif mark[0] == "replace":
            result.append(text[last_end:mark[1]] + mark[3])
            last_end = mark[2]
    result.append(text[last_end:] + '\n\n')
    return ''.join(result)

def response2md(json_dict, text_type: text_type_):
    # 提取文章信息
    author = json_dict['author']['fullname']
    time = json_dict['content_end_info']['create_time_text'][:10]
    question = json_dict["header"]["text"]
    author_url = json_dict["author"]["avatar"]["avatar_image"]["jump_url"]
    article_url = json_dict["header"]["action_url"]
    markdown = f"# {question}\n\n**Author**: [{author}]({author_url})\n\n**Link**: [{article_url}]({article_url})\n\n"
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

        elif segment["type"] == "blockquote":
            markdown += ">"
            markdown += handle_mark(segment["blockquote"]["text"], segment["blockquote"]["marks"])

        elif segment["type"] == "list_node":
            items = segment["list_node"]["items"]
            for i in range(len(items)):
                markdown += f"{i+1}. "
                markdown += handle_mark(items[i]["text"], items[i]["marks"])
                
        elif segment["type"] == "heading":
            markdown += f"{"#" * segment["heading"]["level"]} " 
            markdown += handle_mark(segment["heading"]["text"], segment["heading"]["marks"])

        elif segment["type"] == "hr":
            markdown += "---\n\n"

        elif segment["type"] == "table":
            row_n = segment["table"]["row_count"]
            col_m = segment["table"]["column_count"]
            for i in range(0, row_n):
                for j in range(0, col_m):
                    if j == 0 and segment["table"]["head_column"]:
                        markdown += f"|**{segment["table"]["cells"][i*col_m + j]}**"
                    else :
                        markdown += f"|{segment["table"]["cells"][i*col_m + j]}"
                markdown += "|\n"
                if i == 0:
                    markdown += f"{'|:---' * col_m}|\n"
            markdown += '\n'

        elif segment["type"] == "card":
            if segment["card"]["card_type"] == "link-card":
                markdown += f"[{segment["card"]["title"]}]({segment["card"]["url"]})\n\n"

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
            if segment["image"]["description"]:
                description = f"<center>{segment["image"]["description"]}</center>\n"
            else :
                description = ""            
            markdown += f"![]({img_name}){description}\n\n"

        elif segment["type"] == "code_block":
            markdown += f"```{segment["code_block"]["language"]}\n{segment["code_block"]["content"]}\n```\n\n"
    
    # 知乎想法的图片特殊处理
    if text_type == "pin" and json_dict["image_list"]:
        for image in json_dict["image_list"]["images"]:
            image_index += 1            
            url = image["original_url"]
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
    no_cond = "page-info.zhihu.com" in flow.request.host
    # 域名api.zhihu.com有时候会变成一串ip，不作为参考
    cond1 = "api.zhihu.com" in flow.request.host and ("/answers/" in flow.request.path or "/articles/" in flow.request.path or "/pins/" in flow.request.path)
    cond2 = "/answers/v2" in flow.request.path or "/articles/v2" in flow.request.path or "/pins/v2" in flow.request.path
    if not no_cond and cond2:
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        response_content = flow.response.content
        response_text = response_content.decode('utf-8' )
        data = json.loads(response_text)

        if "/pins/v2" in flow.request.path:
            response2md(data, "pin")
        elif "/articles/v2" in flow.request.path:
            response2md(data, "article")
        elif "/answers/v2" in flow.request.path:
            response2md(data, "answer")            