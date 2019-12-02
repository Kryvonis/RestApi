#RestApi
created by [Artem K.](https://github.com/Kryvonis)

RestApi wrighting on Flask

verison 1.0

- create user: 

```sh
 /api/user method POST. Require two fields -email and -password
```

`/api/user POST
{
"email":"test@gmail.com"
"password":"test"
}`


- get auth token: 

`api/token method GET. Require -email and -password from user`

- 'create post': 

`/api/post method POST. Require one field -title and one optional -body field `

`/api/post POST
{
"title":"Post1"
"body":"Body1"
}`

- 'get users profile': 
 
`/api/user method GET. Require -token or -email and -password`

- 'get users posts': 
 
`/api/posts method GET. Require -token or -email and -password`


- 'get all posts': 

`/api/post/all meghod GET.Require -token or -email and -password. Paging added`

- 'post search': 

`/api/post/search method GET.Require argument -q`

`/api/post/search?q='Pos'`

