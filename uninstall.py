#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform

if __name__ == '__main__':
    match platform.system():
        case "Windows":
            print('Please configure your system to no longer run '
                    '\"...\\quik_setup.bat\" on shell startup.')
        case other:
            if other != 'Linux':
                print('⚠️ Assuming Linux!')
            print('Please remove the \"source .../quik_setup.sh\" from your '
                '~/.bashrc or equivalent.')

    print('💝 Goodbye!')
