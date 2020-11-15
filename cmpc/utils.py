# PSL Packages;
import time
import json
import sys

# PIP Packages;
import requests
import pyautogui
import psutil

# Check if we are on a mac or not
if not sys.platform == 'darwin':
    import pydirectinput
    pydirectinput.FAILSAFE = False


__all__ = (
    'mode_testing',
    'get_git_repo_info',
    'get_size',
    'send_webhook',
    'send_error',
    'move',
    'press',
    'hold',
    'send_data',
)


def mode_testing(environment, env_vars_used, branch):
    """Check if the script is in testing mode based on a number of factors.

    Args:
        environment -- DEPLOY constant from the CONFIG file, should be 'Production' or 'Debug'
        env_vars_used -- bool indicating if CONFIG has been pulled from environment variables
        branch -- the name of the git branch of the repo containing the script, if it exists
    Returns True if script should be in testing mode and False otherwise.
    """
    if environment == 'Debug' or env_vars_used or branch != 'master':
        return True
    else:
        return False


def get_git_repo_info(default_branch_name='master'):
    """Try to get the name of the git branch containing the script.

    Args:
        default_branch_name -- this will be returned as branch_name if there is no git repo
    Returns:
        branch_name
        branch_name_assumed -- True if there was no git repo and branch name defaulted, False otherwise
    """
    try:
        # noinspection PyUnresolvedReferences
        import git
    except ImportError:
        branch_name = default_branch_name
        branch_name_assumed = True
    else:
        try:
            branch_name = git.Repo().active_branch.name
            branch_name_assumed = False
        except (ImportError, git.exc.GitError):
            branch_name = default_branch_name
            branch_name_assumed = True

    return branch_name, branch_name_assumed


def get_size(value, suffix='B'):
    """Scale bytes to its proper format.

    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """

    factor = 1024
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if value < factor:
            return f'{value:.2f}{unit}{suffix}'
        value /= factor


def direct_or_auto():
    """Returns if we should use pydirectinput or pyautogui"""
    platform = sys.platform
    if platform == 'darwin':
        return 'auto'
    else:
        return 'direct'


def send_webhook(url: str, content: str):
    """Sends a webhook to discord, takes (url, message)"""
    data = {'content': content}
    if url == "":
        return
    requests.post(url, data=data)


def send_error(url, error, t_msg, channel, environment, branch, branch_assumed):
    """Sends a error to discord"""
    embed_description = f'***Last Sent Message -*** {t_msg.content}\n\n'\
                        f'***Exception Info -*** {error}\n\n'\
                        f'[***Stream Link***](https://twitch.tv/{channel})\n\n'\
                        f'**Environment -** {environment}'
    if branch != 'master':
        if branch_assumed:
            branch = branch + ' (unknown)'
        embed_description = embed_description + f'\n\n**Branch -** {branch}'

    data = {
        'embeds': [
            {
                'title': 'Script - Exception Occurred',
                'description': embed_description,
                'color': 1107600,
                'footer': {
                    'text': f'User: {t_msg.username} - Channel: {channel}',
                    'icon_url': 'https://blog.twitch.tv/assets/uploads/generic-email-header-1.jpg'
                }
            }
        ]
    }
    requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})


def move(*args, **kwargs):
    """Moves the mouse with cross-platform support"""
    dor = direct_or_auto()
    if dor == 'auto':
        pyautogui.move(*args, **kwargs)
    if dor == 'direct':
        pydirectinput.move(*args, **kwargs)


def press(*args, **kwargs):
    """Presses a key (more functionality coming soon)"""
    pyautogui.press(*args, **kwargs)


def hold(time_value, *args, **kwargs):
    """Holds a key with cross-platform support"""
    dor = direct_or_auto()
    handler = pyautogui
    if dor == 'auto':
        handler = pyautogui
    elif dor == 'direct':
        handler = pydirectinput
    handler.keyDown(*args, **kwargs)
    time.sleep(time_value)
    handler.keyUp(*args, **kwargs)


def send_data(url, context):
    """Dumps machine data, CONFIG, and api"""
    machine_stats = '\n\n'.join([
        f'CPU Frequency: {round(int(psutil.cpu_freq().current) / 1000, 2)} GHz',
        f'Total Usage: {psutil.cpu_percent()}%',
        f'Total Ram: {get_size(psutil.virtual_memory().total)}',
        f'Total Ram Usage: {get_size(psutil.virtual_memory().used)}',
        f'Total Swap: {get_size(psutil.swap_memory().total)}',
        f'Total Swap Usage: {get_size(psutil.swap_memory().used)}',
    ])
    options_str = '\n'.join([
        f"Log All: {context['options']['LOG_ALL']}",
        f"Start Message: {context['options']['START_MSG']}",
        f"EXC_MSG: {context['options']['EXC_MSG']}",
        f"Log PPR: {context['options']['LOG_PPR']}",
        f"Environment: {context['options']['DEPLOY']}",
    ])
    data = {
        'embeds': [
            {
                'title': 'Script Stats',
                'description': f"User: {context['user']}\nChannel: {context['channel']}",
                'fields': [
                    {
                        'name': 'Current API Lists',
                        'value': f"Mod List:\n```\n{context['modlist']}```\n\nDev List:\n```\n{context['devlist']}```",
                    },
                    {
                        'name': 'Script Options',
                        'value': options_str,
                    },
                    {
                        'name': 'Machine Stats',
                        'value': machine_stats,
                    },
                ],
            },
        ],
    }
    requests.post(url, json=data)
