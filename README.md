With the dnspod integration, you can keep your dns records in [DNSPod](dnspod.com) up to date.

# Requirements:
Setup requires an API key created from dnspod

[How to get api key from DNSPod(Chinese Docs)](https://docs.dnspod.cn/account/5f2d466de8320f1a740d9ff3/)


# Configuration

## Example
```yaml
dnspod:
  email: your@email.com
  api_key: api id from dnspod
  api_token: api token from dnspod
  ip_getter:
    external_urls: 
      - https://icanhazip.com
  domains:
    - name: mysite.com
      records: [ www,media,files ]
```

## Intro
`email` (Required) your dnspod user account

`api_key` (Required) api id get from dnspod

`api_token` (Required) api token get from dnspod

`domains` (Required) a list of the domains that you want to update

  `name` (Required) the domain name
	
  `records` (Required) a list of sub-domain records to UPDATE
	
`ip_getter` (Optional) some extra confs to config how to get external ip, the components contains some methods to get it from outside website out of box, so basically you can ignore the confs below.
	
  `external urls` (Optional) some websites you want to get your external ip from, the websites should return a html page contains the ip, just like https://icanhazip.com


# Other Infos

The component get public ip from ipip.net and httpbin.org
You can find other public ip apis from https://icanhazip.com and https://www.ipify.org/

The component will loop to get your public ip every 3 mins and try to update the records if it changed

You can use dnspod.update_records to manually check and update the records
