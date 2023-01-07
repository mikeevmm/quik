#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import platform


def input_bool():
    """Asks the user for a bool (default True)"""
    reply = input('[Y]es/no: ')
    if reply.strip().lower() not in ('n', 'no'):
        return True
    return False


if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.realpath(__file__))

    print('🔍 Making sure a quik.json exists...')

    json_found = False
    
    if (path := os.path.exists(os.path.join(root_dir, 'quik.json'))):
        print('✓ Found it!')
        json_found = True
    else:
        print('❌ Couldn\'t find a quik.json in the default location, '
                'checking for a different location in the environment '
                'variables...')

        if (path := os.environ.get('QUIK_JSON')):
            if os.path.exists(path):
                print('✓ Found it!')
                json_found = True
            print('QUIK_JSON is set, but the file it points to,\n'
                    f'{path}\n'
                    '\tdoes not exist.')

    if not json_found:
        print('❌ Couldn\'t find a quik.json anywhere.\n'
                'Would you like to create one now?')
        if input_bool():
            print(f'⏳ Writing a default quik.json into {path}.')
            try:
                shutil.copy(
                        os.path.join(root_dir, 'internals', 'quik_empty.json'),
                        os.path.join(root_dir, 'quik.json'))
            except:
                print('❌ Something went wrong when writing the default file.')
                print('Please run this script again, or create a quik.json '
                        f'yourself, under {root_dir}.')
                default_path = os.path.join(
                        root_dir, "internals", "quik_empty.json")
                print('You can find a template for how quik.json '
                      'should look in\n'
                       f'{default_path}')
                exit(1)
            print('✓ Done!')
        else:
            print('🤔 Alright, but quik won\'t work without it...')
            print('You can find a template for how quik.json should look in\n'
                    f'{os.path.join(root_dir, "internals", "quik_empty.json")}')
        
    match platform.system():
        case 'Windows':
            cmd_setup_path = os.path.join(root_dir, 'internals', 'quik_setup.bat')
            ps_setup_path = os.path.join(root_dir, 'internals', 'quik_setup.ps1')
            print('Please configure your system to run')
            print(f'\t{cmd_setup_path}')
            print('\t\ton shell startup, if you\'re using Command Prompt, '
                'or add the following line to your PowerShell profile')
            print(f'\t. {ps_setup_path}')
            print('\t\tto dot source the file.')
        case other:
            if other != 'Linux':
                print('⚠️ Assuming a Linux system.')
            print('Please add the following to your ~/.bashrc or equivalent:')
            setup_path = os.path.join(root_dir, 'internals', 'quik_setup.sh')
            print(f"\tsource \"{setup_path}\"")
            print('And then restart your shell for these changes '
                'to take effect:')
            print('\texec $SHELL')

    print('Call \n\tquik --help\n\t\tfor more information.')
    print('💖 Done!')
