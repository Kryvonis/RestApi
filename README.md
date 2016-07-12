# RestApi

verison 1.0


'create user': '/api/user method POST. Require two fields -email and -password',
/api/user POST
{
"email":"test@gmail.com"
"password":"test"
}

'get auth token': 'api/token method GET. Require -email and -password from user',
/api/token GET
{
"token":eyJleHAiOjE0NjgyNzYwNDksImFsZyI6IkhTMjU2IiwiaWF0IjoxNDY4Mjc1NDQ5fQ.eyJpZCI6MX0.zZTMGcs-fr-bT4Bvm124oTeJuiSaw3nBqbBad18_GHo
}

'create post': '/api/post method POST. Require one field -title and one optional -body field ',
/api/post POST
{
"title":"Post1"
"body":"Body1"
}
'get users profile': '/api/user method GET. Require -token or -email and -password',
/api/user GET
{
"id":"1"
"email":"test@gmail.com"
}
'get users posts': '/api/posts method GET. Require -token or -email and -password',
/api/posts GET
{
"posts":
      {
      "title":"Post1"
      "body":"Body1"
      }
}

'get all posts': '/api/post/all meghod GET.Require -token or -email and -password. Paging added',
{
{
  "items": [
  {
      "title":"Post1"
      "body":"Body1"
  }
  ], 
  "meta": {
    "count": 5, 
    "next": "?page=null", 
    "page_count": 1, 
    "previous": "?page=null", 
    "total_count": 1
  }
}

}
'post search': '/api/post/search method GET.Require argument -q'
/api/post/search?q='Pos'
{
"items":[{
        "title":"Post1"
        "body":"Body1"
        }]
}
