import io
import os
import datetime
from PyPDF2 import PdfMerger
from PIL import Image
import fitz  # fitz就是pip install PyMuPDF=1.18.15

# Function：合并pdf
def pdf_merge(pdf_path,pdf_merge_out_path):
    # 实例化pdf合并对象
    merge = PdfMerger()
    # 获取需要合并的pdf文件
    # 获取文件夹中的文件，并按默认顺序排序
    for file_name in sorted(os.listdir(pdf_path)):
        # 找到以pdf结尾的文件
        if file_name.endswith('.pdf'):
            # 拼接文件路径
            filepath=os.path.join(pdf_path,file_name)
            # 合并pdf
            merge.append(filepath)
    merge.write(pdf_merge_out_path)
    merge.close()

# Function：pdf转长图
def pdf_to_long_image(pdf_merge_out_path, long_image_out_path):
    doc = fitz.open(pdf_merge_out_path)
    images = []
    width = 0
    height = 0

    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        width = max(width, pix.width)
        height += pix.height
        images.append(img)

    long_image = Image.new('RGB', (width, height))
    y_offset = 0

    for img in images:
        long_image.paste(img, (0, y_offset))
        y_offset += img.height

    long_image.save(long_image_out_path)

# Function：pdf转图片，转为一张一张的图片
def pdf_to_images(pdf_merge_out_path, imagePath):
    startTime_pdf2img = datetime.datetime.now()  # 开始时间

    print("imagePath=" + imagePath)
    pdfDoc = fitz.open(pdf_merge_out_path)
    for pg in range(pdfDoc.pageCount): # .pageCount方法需要PyMuPDF版本为1.18.15才可适用
        page = pdfDoc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        zoom_x = 1.33333333  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.33333333
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)

        if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
            os.makedirs(imagePath)  # 若图片文件夹不存在就创建

        pix.writePNG(imagePath + '/' + 'images_%s.png' % pg)  # 将图片写入指定的文件夹内

    endTime_pdf2img = datetime.datetime.now()  # 结束时间
    print('pdf2img时间=', (endTime_pdf2img - startTime_pdf2img).seconds)

# Function：合并图片为长图
def images_merge(imagePath, output_path):
    image_files = sorted([file for file in os.listdir(imagePath) if file.endswith(('.jpg', '.jpeg', '.png'))])

    if not image_files:
        print("No image files found in the folder.")
        return

    images = []
    total_height = 0
    max_width = 0

    for image_file in image_files:
        image_path = os.path.join(imagePath, image_file)
        image = Image.open(image_path)
        images.append(image)

        total_height += image.height
        max_width = max(max_width, image.width)

    merged_image = Image.new('RGB', (max_width, total_height), (255, 255, 255))
    y_offset = 0

    for image in images:
        merged_image.paste(image, (0, y_offset))
        y_offset += image.height

    merged_image.save(output_path, dpi=(300,300))
    print(f"Merged image saved as {output_path}")

# Function：图片转为pdf
def image_to_pdf(image_path, pdf_path):
    image = Image.open(image_path)

    # 将图像转换为PDF
    image.save(pdf_path, "PDF" ,resolution=300.0)

    print(f"Image converted to PDF and saved as {pdf_path}")


if __name__ == "__main__":
    # pdf path
    pdf_path = './pdf_path'
    pdf_merge_out_path= './pdf_merge_out_path/merge_output.pdf'
    long_image_out_path = './image_output_path/long_image_output1.png'
    imagePath = './imagePath'
    merged_image_path = './image_output_path/merged_image.jpg'
    image_to_pdf_path='./pdf_path/merged_image.pdf'
    # 调用pdf合并的方法
    pdf_merge(pdf_path, pdf_merge_out_path)

    # 调用PDF转长图的方法
    pdf_to_long_image(pdf_merge_out_path, long_image_out_path)

    # 调用pdf转图片的方法
    pdf_to_images(pdf_merge_out_path, imagePath)

    # 调用合并图片的方法
    images_merge(imagePath, merged_image_path)

    # 调用图片转为pdf的方法
    image_to_pdf(merged_image_path, image_to_pdf_path)