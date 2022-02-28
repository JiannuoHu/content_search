from ma_trigger.scrapper import scrape_website
import json

def convert_to_slack_block(slack_dict):

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

if __name__ == "__main__":
    website_names = ['reuters', 'nyt','wsj','themiddlemarket']

    with open("elephants.json") as f:
        elephants = json.load(f)

    res_list = []
    for web in website_names:
        results = scrape_website({'website': web, "elephants":elephants}, None)
        res_list.append(results)


    for result in res_list:
        if result['app_success']!='success':
            tell_slack(result['app_success'])


    have_results  = [result for result in res_list if result['app_success']=='success']


    slack_dict = {}
    slack_dict['content'] = []
    slack_dict['error'] = []

    for each_web_result in res_list:
        try:
            for each_record in each_web_result['records']: # if we found news for target clients
                if slack_dict['content'] !=[]:
                    if each_record['company'] in [i['company'] for i in slack_dict['content']]:
                        for i in slack_dict['content']:
                            if each_record['company'] == i['company'] and each_record['news'] not in i['news']:
                                i['news'].extend(each_record['news'])
                    else:
                        slack_dict['content'].append(each_record)
                else:
                    slack_dict['content'].append(each_record)
    
        except:
            if "change the html settings" in each_web_result['app_success']: # if failure
                slack_dict['error'].append(each_web_result['app_success'])

            else:
                pass # no action if we have news but not relate to our target clients

    if slack_dict['content']: # if we found news
        slack_dict['message'] = 'Here are the important m&a news for the past 1 week.'
        slack_dict['error'] = ", ".join(slack_dict['error'])

        if slack_dict['error'] == '': # if no error
            del slack_dict['error']
    
    if slack_dict['error'] and not slack_dict['content']: # if no news but only error
        slack_dict['message'] = "Doing maintenance work, will update soon"
        slack_dict['error'] = ", ".join(slack_dict['error'])
        del slack_dict['content']
    
    if not slack_dict['error'] and not slack_dict['content']: # if no news and no error
        slack_dict['message'] = 'No important m&a news found for the past 1 week.'
        del slack_dict['content']
        del slack_dict['error']

    slack_json = convert_to_slack_block(slack_dict)
            
    print(slack_json)