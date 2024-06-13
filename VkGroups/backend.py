import vk_api
import pandas as pd
import requests


def get_group_id(group_name, access_token):
    url = 'https://api.vk.com/method/utils.resolveScreenName'
    params = {
        'screen_name': group_name,
        'access_token': access_token,
        'v': '5.131'
    }
    with requests.get(url, params=params) as response:
        data = response.json()
        if 'response' in data and data['response']['type'] == 'group':
            return data['response']['object_id']
        else:
            raise ValueError(f"Error fetching group ID: {data}")


def get_group_members(group_id, access_token):
    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()

    members = []
    offset = 0
    count = 1000

    while True:
        response = vk.groups.getMembers(group_id=group_id, offset=offset, count=count, fields='id,first_name,last_name,bdate,country,home_town,sex,domain,education,personal')
        members.extend(response['items'])
        offset += count
        print(f"{response["count"]}/{offset}")
        if offset >= response['count']:
            break

    return members


def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')


group_name = "kriper2004"
access_token = 'af994a41af994a41af994a41a0ac81d19caaf99af994a41c9f125026e10d960d0daabc8'
group_id = get_group_id(group_name, access_token)
print(group_id)

open("../test_users.csv", "w").close()
members = get_group_members(group_id, access_token)
save_to_csv(members, "../test_users.csv")
print(members)
print(f"Total members: {len(members)}")