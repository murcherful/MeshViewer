import os 
from nicegui import app, ui
import re
import math
import copy

ui.add_body_html('''
<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"></script>
''')
ui.add_css('''
    .my_label {
        word-break:break-all;
    }
    .my_html {
        aspect-ratio: 1;
        width: 100%;
        height: 100%;
    }
    .my_input {
        width: 800px;
    }
    .my_button {
        width: 100%;
    }
''')

@ui.page('/view/{file_name}')
def view_file(file_name):
    ui.page_title('Mesh Viewer')
    dark = ui.dark_mode()
    dark.enable()
    with ui.row():
        ui.markdown('#### Mesh Viewer')
        ui.switch('Dark mode').bind_value(dark)
        ui.markdown('@ murcherful 2025.7')
    file_name = file_name.replace('@@@','/')
    if check_suffix(file_name, support_3d_suffix):
        ui.add_body_html('''
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"></script>
        ''')
        with ui.column(align_items='center').classes('w-full'):
            ui.html(f'''<model-viewer style="width: 1200px; height: 1200px;" src="/models/{file_name}" alt="A 3D model" auto-rotate camera-controls shadow-intensity="1"></model-viewer>''')
            ui.label(f'{file_name}').classes('my_label')
    elif check_suffix(file_name, support_2d_suffix):
        with ui.column(align_items='center').classes('w-full'):
            ui.image(f'/models/{file_name}').style('width: 1200px')
            ui.label(f'{file_name}').classes('my_label')

ui.page_title('Mesh Viewer')
gcolumn = ui.column()
dark = ui.dark_mode()
dark.enable()
with gcolumn:
    with ui.row():
        ui.markdown('#### Mesh Viewer')
        ui.switch('Dark mode').bind_value(dark)
        ui.markdown('@ murcherful 2025.7')
    ui.markdown('Use "" to filter file name. Use $$ to exclude file name. For example "aa" $bb$ will show all files containing "aa" but not containing "bb".')
    head_row = ui.row(align_items='baseline')
    info_label = ui.label('Current directory: None. Filter: None.')

with head_row:
    path_input = ui.input(label='Path').classes('my_input')
    filter_input = ui.input(label='Filter')
    column_num_input = ui.number(label='Column', min=1, max=10, step=1, value=5)
    row_num_input = ui.number(label='Row', min=1, max=10, step=1, value=2)

page_row = None 
grid_view = None 
file_list = []
support_3d_suffix = ['.obj', '.glb', '.gltf', '.stl', '.ply']
support_2d_suffix = ['.png', '.jpg']
support_suffix = support_3d_suffix + support_2d_suffix

def check_suffix(file_name, suffix_list):
    for suffix in suffix_list:
        if file_name.endswith(suffix):
            return True
    return False

def process_filter_str(filter_str):
    pattern_pos = r'"(.*?)"'
    pattern_nag = r'\$(.*?)\$'
    pos = re.findall(pattern_pos, filter_str)
    nag = re.findall(pattern_nag, filter_str)
    return pos, nag

def filter_file_name(file_name, pos, nag):
    if not check_suffix(file_name, support_suffix):
        return False
    for p in pos:
        if p not in file_name:
            return False
    for n in nag:
        if n in file_name:
            return False
    return True

def get_all_files(dir_path, filter_str):
    files = []
    pos, nag = process_filter_str(filter_str)
    for file_name in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, file_name)):
            files.extend(get_all_files(os.path.join(dir_path, file_name), filter_str))
        else:
            if filter_file_name(file_name, pos, nag):
                files.append(os.path.join(dir_path, file_name))
    return files

def page_change(page):
    global grid_view
    col_num = int(column_num_input.value)
    row_num = int(row_num_input.value)
    page_item_num = col_num * row_num
    if grid_view is not None:
        grid_view.delete()
    with gcolumn:
        grid_view = ui.grid(rows=row_num, columns=col_num)
    current_page = page.value
    current_files = file_list[page_item_num*(current_page-1):page_item_num*current_page]
    with grid_view:
        for file_name in current_files:
            with ui.card().tight():
                if check_suffix(file_name, support_3d_suffix):
                    ui.html(f'''<model-viewer class="my_html" src="/models/{file_name}" alt="A 3D model" auto-rotate camera-controls shadow-intensity="1"></model-viewer>''').classes('my_html')
                elif check_suffix(file_name, support_2d_suffix):
                    ui.image(f'/models/{file_name}').classes('my_html')
                with ui.card_section().classes('my_label'):
                    ui.label(file_name)
                with ui.grid(rows=1, columns=2).classes('my_button'):
                    with ui.column(align_items='center'):
                        ui.link('view', f'/view/{file_name.replace("/", "@@@")}', new_tab=True)
                    with ui.column(align_items='center'):
                        ui.link('download', f'/models/{file_name}')


def get_files():
    global page_row, grid_view, file_list
    dir_path = path_input.value if path_input.value != '' else 'None'
    filter_str = filter_input.value if filter_input.value != '' else 'None'
    if page_row is not None:
        page_row.delete()
    if grid_view is not None:
        grid_view.delete()
    if file_list is not None:
        file_list = None
    
    if dir_path == 'None':
        info_label.set_text('Current directory: None. Filter: None.')
        return 
    file_list = get_all_files(dir_path, filter_str)
    old_file_list = copy.deepcopy(file_list)
    dir_path_len = len(dir_path)
    file_list = [file_name[dir_path_len+1:] for file_name in file_list]
    if len(file_list) == 0:
        ui.notify('No file found.')
        return
    # app.add_static_files('/models', dir_path)
    for i in range(len(file_list)):
        new_file_name = file_list[i]
        old_file_name = old_file_list[i]
        app.add_static_file(url_path=f'/models/{new_file_name}', local_file=old_file_name)

    file_num = len(file_list)
    
    col_num = int(column_num_input.value)
    row_num = int(row_num_input.value)
    page_number = file_num // (col_num * row_num) + 1
    page_item_num = col_num * row_num

    info_label.set_text(f'Current directory: {dir_path}. Filter: {filter_str}. Get {file_num} files. Max page: {page_number}.')

    with head_row:
        page_row = ui.row(align_items='baseline')
    with page_row:
        p = ui.pagination(1, page_number, direction_links=True, on_change=page_change)
    with gcolumn:
        grid_view = ui.grid(rows=row_num, columns=col_num)
    current_page = 1
    current_files = file_list[page_item_num*(current_page-1):page_item_num*current_page]
    with grid_view:
        for file_name in current_files:
            with ui.card().tight():
                if check_suffix(file_name, support_3d_suffix):
                    ui.html(f'''<model-viewer class="my_html" src="/models/{file_name}" alt="A 3D model" auto-rotate camera-controls shadow-intensity="1"></model-viewer>''').classes('my_html')
                elif check_suffix(file_name, support_2d_suffix):
                    ui.image(f'/models/{file_name}').classes('my_html')
                with ui.card_section().classes('my_label'):
                    ui.label(file_name)
                with ui.grid(rows=1, columns=2).classes('my_button'):
                    with ui.column(align_items='center'):
                        ui.link('view', f'/view/{file_name.replace("/", "@@@")}', new_tab=True)
                    with ui.column(align_items='center'):
                        ui.link('download', f'/models/{file_name}')

with head_row:
    ui.button('Go!', on_click=get_files)


ui.run(port=8081)
