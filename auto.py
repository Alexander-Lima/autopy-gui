from tkinter import *
import pyautogui as auto
import tkinter as tk
from pyperclip import *
import pyperclip as clip
import keyboard as kb
import time

queue = []
timer_counter = 3
options_list = [
    'BAIXO',
    'CIMA',
    'ESQUERDA',
    'DIREITA',
    'ENTER',
    'ESC',
    'PAUSE',
    'ESCREVER',
    'RELACIONAL']
tests_operators = ['=','<','>','<>','<=','>=']

def execute(time_pause, repeat_times):
    initial_time = time.perf_counter()
    if queue.__len__() == 0:
        auto.alert(text='Colete ao menos um comando!', title='AVISO!', button='OK')
        return
    if time_pause.get() == '':
        auto.alert(text='Digite o tempo entre os comandos!', title='AVISO!', button='OK')
        return
    if repeat_times.get() == '':
        auto.alert(text='Digite a quantidade de repetições!', title='AVISO!', button='OK')
        return

    for i in range(0, int(repeat_times.get())):
        if kb.is_pressed('ctrl'):
            auto.alert(text='Execução encerrada pelo usuário!')
            break 
        for command in reversed(queue):
            match command['type']:
                case 'click':
                    auto.click(command['data'])
                case 'pause':
                    time.sleep(command['data'])
                case 'write':
                        auto.write(command['data'])
                case 'relational':
                    test_condition_option(operator=command['data'][0], entry=command['data'][1])
                case 'copy':
                    auto.hotkey('ctrl','c')
                case 'paste':
                    auto.hotkey('ctrl','v')
                case 'key':
                    keys_map = {
                        'CIMA': 'UP',
                        'BAIXO': 'DOWN',
                        'ESQUERDA': 'LEFT',
                        'DIREITA': 'RIGHT'
                    }
                    if(command['data'] in keys_map.keys()):
                        auto.press(keys_map[command['data']])
            auto.PAUSE = float(time_pause.get())
    time_elapsed = time.perf_counter() - initial_time
    auto.alert(
        text=f'Rotina finalizada! \nTempo total: {str(time_elapsed.__round__(1))} segundos.', 
        title='AVISO!', 
        button='OK')

def capture(command_counter, commands_list):
    add_item_to_stack({'type': 'click', 'data': auto.position()})
    update_command_counter(command_counter, commands_list)

def function_detected(
        window, 
        command_counter, 
        selected_option, 
        test_option_dropdown, 
        pause_time, 
        entry_condition,
        commands_list):
    reset(test_option_dropdown, pause_time, entry_condition)

    match selected_option.get():
        case 'RELACIONAL':
            test_option_dropdown.config(state='normal', background='white')
        case 'PAUSE':
            pause_time.grid(
                column=0, 
                row=2, 
                sticky='E', 
                ipady='2', 
                padx=30)
        case 'ESCREVER':
            popup_win(command_counter, commands_list)
            selected_option.set(options_list[0])
        case 'CL.LIVRE':
            create_timer(window, commands_list)

def reset(test_option_dropdown, pause_time, entry_condition):
    test_option_dropdown.config(state='disabled', background='#ABB2B9')
    disable_test(entry_condition)
    pause_time.delete(0,'end')
    pause_time.grid_remove()

def create_timer(command_counter, commands_list):
    global timer_counter
    timer_counter = 3
    window_timer = tk.Tk()
    window_timer.overrideredirect(True)
    window_timer.config(
        highlightbackground="black",
        highlightthickness="4",
        background='white')
    
    window_timer.geometry(set_window_coordinates(window_timer, 125, 125))

    labeltimer = tk.Label(
        window_timer, 
        text= timer_counter, 
        padx=55, 
        pady=10)
    
    labeltimer.config(font=("Calibri",44), background='white')
    labeltimer.pack()
    window_timer.after(0, change_text(label=labeltimer, window=window_timer))
    window_timer.after(3, capture(command_counter, commands_list))
    window_timer.mainloop()
    
def change_text(label: tk.Label, window:tk):
    global timer_counter
    label.config(text=timer_counter, font=('Helvetica','50', 'bold'))
    if timer_counter < 0: 
        window.destroy()
        return
    elif timer_counter == 0:
        label.config(text='OK!', font=('Helvetica','40', 'bold'), pady=30)
    label.update()
    timer_counter -= 1
    time.sleep(1)
    change_text(label, window)

def add_command(command_counter, commands_list, command):
    if command['type'] == 'clear':
        queue.clear()
        auto.alert(text='Lista de comandos apagada!', title='AVISO!', button='OK')
    else:
        add_item_to_stack(command)
    update_command_counter(command_counter, commands_list)

def set_window_coordinates(window, width, height):
    x = int((window.winfo_screenwidth() - width)/2)
    y = int((window.winfo_screenheight() - height)/2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def save_command(option, pause_time, entry_condition, test_option, command_counter, commands_list):
    match option.get():
        case 'PAUSE':
            if pause_time.get() == '':
                return auto.alert(text='Digite o tempo de pausa!', title='AVISO!', button='OK')
            add_item_to_stack({'type': 'pause', 'data': float(pause_time.get())})
        case 'RELACIONAL':
            if entry_condition.get() == '':
                return auto.alert(text='Insira uma operação relacional!', title='AVISO!', button='OK') 
            add_item_to_stack({'type': 'relational', 'data': [test_option.get(), entry_condition.get()]})
        case _:
            add_item_to_stack({'type': 'key', 'data': option.get()})
    update_command_counter(command_counter, commands_list)

def add_item_to_stack(command_dict):
    replace_items_indexes = [index for index, command 
                             in enumerate(queue) if command["type"] == "replace"]

    if(replace_items_indexes.__len__() == 0):
        queue.insert(0, command_dict)
        return auto.alert(text='Comando acidionado!', title='AVISO!', button='OK') 
    
    for index in replace_items_indexes:
        queue[index] = command_dict
    auto.alert(text='Comandos substituídos!', title='AVISO!', button='OK')

def update_commands_list(commands_list: tk.Listbox):
    commands_list.delete(0, commands_list.index("end"))
    for i, item in enumerate(queue):
        commands_list.insert(i, f'  {get_description(item)}')

def get_description(item):
    item_map = {
        'pause': f'PAUSA ({item.get("data", "")} segundos)',
        'relational': get_relational_expression_text(item),
        'key': f'TECLA ({item.get("data", "")})',
        'write': f'ESCREVER ({item.get("data", "")})',
        'copy': 'COPIAR',
        'paste': 'COLAR',
        'click': get_click_text(item),
        'replace': '--SUBSTITUIR--' 
    }
    return item_map[item['type']]

def get_relational_expression_text(item):
    if(item.get("data", None) and item['type'] == 'relational'):
        return f'RELACIONAL (X {str(item["data"][0]) + " " + str(item["data"][1])})'
    return ""

def get_click_text(item):
    if(item.get("data", None) and item['type'] == 'click'):
        return f'CLIQUE ({"X=" + str(item["data"].x) + ", Y=" + str(item["data"].y)})'
    return ""

def popup_win(command_counter, commands_list):
    write = auto.prompt('DIGITE A FRASE QUE DESEJA ESCREVER:')
    if write != None and write != '':
        add_item_to_stack({'type': 'write', 'data': write})
        update_command_counter(command_counter, commands_list)
    elif write == '':
        auto.alert(text='Digite um texto!', title='AVISO!', button='OK')
        popup_win(command_counter, commands_list)

def update_command_counter(command_counter, commands_list):
    command_counter.config(text=f'COMANDOS NA FILA: {str(queue.__len__())}')
    update_commands_list(commands_list)

def delete_selected_commands(command_counter, commands_list):
    if queue.__len__() > 0:
        remove_selected_items(commands_list)
        update_command_counter(command_counter, commands_list)
    else:
        auto.alert(text='A lista de comandos está vazia!', title='AVISO!', button='OK')

def remove_selected_items(commands_list):
    global queue
    selected_commands_index = commands_list.curselection()
    if selected_commands_index.__len__() == 0:
         auto.alert(text='Selecione um comando da lista!', title='AVISO!', button='OK')
         return
    queue = [item for index, item in enumerate(queue) if index not in selected_commands_index]

def enable_test(selected, entry_condition):
    if selected == ' ':
        disable_test(entry_condition)
    else:
        entry_condition.config(state='normal')

def test_condition_option(operator, entry):
    clip.copy('')
    auto.hotkey('ctrl','c')
    clipboard = clip.paste().replace("b'",'').replace("\r\n",'')

    if clipboard == '' or clipboard == None:
        auto.alert(text='Não foi possivel capturar um valor no clipboard!', title='AVISO!', button='OK')
        return
    
    clipboard = int(clipboard)
    value = int(entry)
    logic_operations = {
        '=': clipboard == value,
        '>=': clipboard >= value,
        '<=': clipboard <= value,
        '>': clipboard > value,
        '<': clipboard < value,
        '<>': clipboard != value,
    }
    if(not logic_operations[operator]):
        auto.alert(text= 'Resultado da expressão lógica é falso!', title='AVISO!', button='OK') 

def disable_test(entry_condition):
    entry_condition.delete(0, 'end')
    entry_condition.config(state='disabled')

def replace_command(commands_list):
    current_selection = commands_list.curselection()
    if(current_selection.__len__() == 0):
        return 
    if(current_selection.__len__() > 1):
        return auto.alert(text= 'Selecione apenas um item!', title='AVISO!', button='OK')
    queue[current_selection[0]] = {'type': 'replace'}
    update_commands_list(commands_list)

def create_window():
    window = tk.Tk()
    window.title('BY ALEXANDER')
    set_window_coordinates(window=window, width=332, height=770)
    window.config(
        highlightbackground="black",
        highlightthickness="2",
        background='blue')
    window.resizable(height=0, width=0)
    return window

def add_widgets(window):
    text = tk.Label(
        window,
        text='SELECIONE UMA OPÇÃO:',
        font=('bold'),
        background='blue',
        foreground='white',
        width=24)
    
    text.grid(
        column=0,
        row=0, 
        columnspan=2, 
        pady=10, 
        padx=5)
    
    command_counter = tk.Label(
        window, text='COMANDOS NA FILA: 0', 
        font=('bold'), 
        background='blue', 
        foreground='white')
    
    command_counter.grid(
        column=0, 
        row=12, 
        columnspan='2', 
        pady=10)

    collect = tk.Button(
        window,
        text='CLICAR',
        command=lambda: create_timer(command_counter, commands_list),
        borderwidth='5')
    
    collect.grid(
        column=0, 
        row=1, 
        pady=10, 
        padx=10, 
        sticky='W')
    
    collect.config(
        height='1',
        width='10',
        background='white',
        foreground='black', 
        font=('Helvetica','10', 'bold'))

    copy_text = tk.Button(
        window, 
        text='COPIAR', 
        command=lambda: add_command(command_counter, commands_list, {'type': 'copy'}))

    copy_text.grid(
        column=1, 
        row=1, 
        pady=10, 
        padx=5, 
        sticky='W')
    
    copy_text.config(
        height='1', 
        width='10', 
        background='white', 
        foreground='black', 
        font=('Helvetica','10', 'bold'), 
        borderwidth='5')
    
    entry_condition = tk.Entry(window)
    entry_condition.config(
        width='10', 
        borderwidth='3', 
        relief='sunken', 
        state='disabled', 
        disabledbackground='#ABB2B9')
    
    entry_condition.grid(
        column=1,
        row=7, 
        pady=10, 
        padx=5)

    selected_option = tk.StringVar()
    selected_option.set(options_list[0])
    option_menu = tk.OptionMenu(
        window, 
        selected_option, 
        *options_list, 
        command=lambda x: function_detected(
            window,
            command_counter, 
            selected_option, 
            test_option_dropdown, 
            pause_time, 
            entry_condition,
            commands_list))

    option_menu.config(
        width='6', 
        font=('Helvetica','10','bold'), 
        background='white',
        anchor='w')
    
    option_menu.grid(
        column=0,
        row=2, 
        pady=10, 
        padx=10, 
        sticky='W')

    pause_time = tk.Entry(
        window, 
        font=('Helvetica','10','bold'),
        background='white', width='3', 
        borderwidth='3', 
        relief='sunken')

    paste_text = tk.Button(
        window, 
        text='COLAR', 
        command=lambda: add_command(command_counter, commands_list, {'type': 'paste'}))

    paste_text.grid(
        column=1, 
        row=2, 
        pady=10, 
        padx=5, 
        sticky='W')
    
    paste_text.config(
        height='1', 
        width='10', 
        background='white', 
        foreground='black', 
        font=('Helvetica','10', 'bold'), 
        borderwidth='5')
    
    commands_list = tk.Listbox(window)
    commands_list.config(
        width=35,
        height=5,
        selectmode=MULTIPLE)
    commands_list.bind('<Double-1>', lambda event: replace_command(commands_list))

    commands_list.grid(
        column=0,
        columnspan=2,
        row=13,
        sticky='w',
        padx=23,
        pady=10)

    capture_command = tk.Button(
        window, 
        text='GRAVAR COMANDO', 
        command=lambda: save_command(
            selected_option,
            pause_time, entry_condition, 
            test_option, 
            command_counter,
            commands_list))

    capture_command.config(
        height='1', 
        width='30', 
        background='white', 
        foreground='black', 
        font=('Helvetica','10', 'bold'), 
        borderwidth='5')
    
    capture_command.grid(
        column=0, 
        row=4, 
        columnspan=2, 
        pady=10, 
        padx=7, 
        sticky='W')

    capture_command = tk.Button(
        window, 
        text='REMOVER COMANDOS', 
        command=lambda: delete_selected_commands(command_counter, commands_list))

    capture_command.config(
        height='1', 
        width='30', 
        background='white', 
        foreground='black', 
        font=('Helvetica','10', 'bold'), 
        borderwidth='5')
    
    capture_command.grid(
        column=0, 
        row=5, 
        columnspan=2, 
        pady=10, 
        padx=7, 
        sticky='W')

    text_condition = tk.Label(
        window, 
        text='TESTAR CONDIÇÃO:', 
        font=('bold'), 
        background='blue', 
        foreground='white', 
        width=24)
    
    text_condition.grid(
        column=0,
        row=6, 
        columnspan=2, 
        pady=10, 
        padx=5)

    test_option = tk.StringVar()
    test_option.set(tests_operators[0])
    test_option_dropdown = tk.OptionMenu(
        window, 
        test_option, 
        *tests_operators, 
        command=lambda option: enable_test(option, entry_condition))
    
    test_option_dropdown.config(
        width='1', 
        font=('Helvetica','10','bold'), 
        background='#ABB2B9', 
        state='disabled')
    
    test_option_dropdown.grid(
        column=0,
        row=7, 
        pady=10, 
        padx=35,
        sticky='w')

    text_pause = tk.Label(
        window, 
        text='TEMPO ENTRE \n COMANDOS (seg.)', 
        font=('bold'), 
        background='blue', 
        foreground='white')
    
    text_pause.grid(
        column=0,
        row=8, 
        pady=10, 
        padx=5)

    time_pause = tk.Entry(window)
    time_pause.config(
        width='10',
        borderwidth='3', 
        relief='sunken')
    
    time_pause.grid(
        column=1,
        row=8, 
        rowspan=2, 
        pady=25, 
        sticky='n', 
        padx=5)

    text_repeat = tk.Label(
        window, 
        text='REPETIÇÕES', 
        font=('bold'), 
        background='blue', 
        foreground='white', 
        borderwidth='5')
    
    text_repeat.grid(
        column=0,
        row=9, 
        pady=10, 
        padx=10, 
        sticky='w')

    repeat_times = tk.Entry(window)
    repeat_times.config(
        width='10', 
        borderwidth='3', 
        relief='sunken')
    
    repeat_times.grid(
        column=1,
        row=9, 
        pady=10, 
        padx=30,
        sticky='e')

    restart = tk.Button(
        window, 
        text='REINICIAR', 
        command=lambda: add_command(command_counter, commands_list, {'type': 'clear'}))
    
    restart.config(
        height='1', 
        width='10', 
        background='white',
        foreground='black', 
        font=('Helvetica','10', 'bold'), 
        borderwidth='5')
    
    restart.grid(
        column=0, 
        row=10, 
        pady=10,
        padx=15, 
        sticky='W')

    execute_button = tk.Button(
        window, 
        text='EXECUTAR', 
        command=lambda: execute(time_pause, repeat_times))
    
    execute_button.config(
        height='1', 
        width='10', 
        background='white', 
        foreground='black', 
        font=('Helvetica','10', 'bold'), 
        borderwidth='5')
    
    execute_button.grid(
        column=1, 
        row=10, 
        pady=10, 
        padx=5, 
        sticky='W')

def start():   
    window = create_window()
    add_widgets(window)
    window.mainloop()

if __name__ == '__main__':
    start()
