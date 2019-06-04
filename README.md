需要说明的是：
1、此次的响应的数为 Json
2、请求为 Ajax POST 请求
3、请求的参数为 request payload 类型 ，具体的请自行百度它与 formdata 这种参数传递时的区别
4、发送参数时一定注意不能使用 FormRequest 发送，这个只是适用于 formdata 这种参数类型
5、此次在发送请求参数时采用了 Request 的发送方法，在使用时特别需要注意的时以下几点：
    1、Content-Type  必须使用：application/json;charset=UTF-8
    2、参数传递使用 body= json类型的参数（json.dumps，把该参数变成json格式的数据）
    3、method= 'POST'
    4、注意其中一些参数是 null的 和 None 的，这个视情况而定，此次的参数没有的按照浏览器抓包的结果 作为 ""  空处理了
6、另外走的一个冤枉路就是：有时候参数全部携带不一定是一件好事儿，有时候偏偏获取不到数据,此次如果不携带Authorization只能获取一页的数据，cookies 中有一项 juzi_token 值