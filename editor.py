import cv2
import glob
import os
import json

# 画像ディレクトリのパス
image_dir = r'D:\Pictures\splatoon3-results'

# 画像ファイルのパスを取得
image_paths = glob.glob(os.path.join(image_dir, '*.jpg'))

# 画像を読み込み
images = [cv2.imread(image_path) for image_path in image_paths]

drawing = False


# すべての画像が同じサイズであることを確認
first_image_shape = images[0].shape
for image in images:
    if image.shape != first_image_shape:
        raise ValueError("すべての画像が同じサイズではありません。")

def save_data_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_data_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def draw_areas_on_image(image, areas, aspect_ratio):
    for area in areas:
        start_point = (int(area['topleft'][0] * aspect_ratio), int(area['topleft'][1] * aspect_ratio))
        end_point = (int(area['bottomright'][0] * aspect_ratio), int(area['bottomright'][1] * aspect_ratio))
        cv2.rectangle(image, start_point, end_point, (0, 255, 0), 2)

# リサイズされた画像を表示し、元の画像のサイズに合わせて座標を取得
def resize_image(image, height):
    aspect_ratio = height / image.shape[0]
    width = int(image.shape[1] * aspect_ratio)
    return cv2.resize(image, (width, height)), aspect_ratio

# マウスコールバック関数
def select_roi(event, x, y, flags, param):
    global start_point, end_point, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)
            temp_image = param['image'].copy()
            cv2.rectangle(temp_image, start_point, end_point, (0, 255, 0), 2)
            cv2.imshow('First Image', temp_image)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        original_start_x = int(start_point[0] / param['aspect_ratio'])
        original_start_y = int(start_point[1] / param['aspect_ratio'])
        original_end_x = int(end_point[0] / param['aspect_ratio'])
        original_end_y = int(end_point[1] / param['aspect_ratio'])
        name = input("データの名前 :  ")
        if name == "":
            return
        if any(area['name'] == name for area in data['areas']):
            print("名前が重複しています。")
            return
        print(f"{name} : ([{original_start_x}, {original_start_y}], [{original_end_x}, {original_end_y}])")
        data['areas'].append({
            'name': name,
            'topleft': [original_start_x, original_start_y],
            'bottomright': [original_end_x, original_end_y]
        })
        draw_areas_on_image(edit_image, data['areas'], aspect_ratio)
        cv2.imshow('First Image', edit_image)

data = load_data_from_json('data.json')
# 一枚目の画像をリサイズして表示
edit_image, aspect_ratio = resize_image(images[0], 900)

# areasを画像に描画
draw_areas_on_image(edit_image, data['areas'], aspect_ratio)

cv2.imshow('First Image', edit_image)
cv2.setMouseCallback('First Image', select_roi, {'aspect_ratio': aspect_ratio, 'image': edit_image})

cv2.waitKey(0)
cv2.destroyAllWindows()

save_data_to_json(data, 'data.json')

# 画像を保存
cv2.imwrite('edited_image.jpg', edit_image)