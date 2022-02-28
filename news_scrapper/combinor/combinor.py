import json

def slack_json_builder(slack_dict):

    message = {
        "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": slack_dict['message']
                        }
                    }
                ]
            }

    if 'content' in slack_dict.keys():

        content_list = slack_dict['content']
        
        for each_content in content_list:
            message['blocks'].append({'type':'divider'})
            one_block = list(each_content.values())

            company_info = one_block[:3]
            company_info[0] = "*" + company_info[0] + "*"
            news = one_block[3]

            num_space = (len(company_info) - len(news))
            num_space_list = [' '] * num_space

            if num_space>0:
                news.extend(num_space_list)
            elif num_space<0:
                company_info.extend(num_space_list)
            
            fields = []
            
            for i in range(len(company_info)):
                fields.append({"type":"mrkdwn", "text": company_info[i]})
                fields.append({"type":"mrkdwn", "text": news[i]})
            
            message['blocks'].append({"type": "section", "fields":fields})

    return json.dumps(message)

def slack_error(message):

    slack_dict = {}
    slack_dict['message'] = message
    slack_json = slack_json_builder(slack_dict)
    
    return print(slack_json)

def slack_success(slack_dict):

    slack_json = slack_json_builder(slack_dict)
    
    return print(slack_json)

def combinor(event, context):

    res_list = event

    for result in res_list:
        if result['app_success']!='success':
            slack_error(result['app_success'])

    have_results  = [result for result in res_list if result['app_success']== 'success']

    if have_results !=[]:
        slack_dict = {'content':[]}

        for each_web_result in have_results:
            for each_record in each_web_result['records']:
                if slack_dict['content'] !=[]:
                    if each_record['company'] in [i['company'] for i in slack_dict['content']]:
                        for i in slack_dict['content']:
                            if each_record['company'] == i['company'] and each_record['news'] not in i['news']:
                                i['news'].extend(each_record['news'])
                    else:
                        slack_dict['content'].append(each_record)
                else:
                    slack_dict['content'].append(each_record)

        slack_dict['message'] = 'Here are the important m&a news for the past 1 week.'
        slack_success(slack_dict)