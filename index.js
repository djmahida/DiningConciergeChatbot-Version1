var chatHistory = [];

var url_string = window.location.href;
var cognito_token = url_string.substring(url_string.indexOf("=") + 1,url_string.indexOf("&"));


AWS.config.region = 'us-east-1'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'ENter user_pool_id',
	Logins: {
	   'cognito-idp.us-east-1.amazonaws.com/us-east-1_F92Il7a5T': cognito_token
	}
});

// AWS.config.region = 'us-east-1'; // Region
// AWS.config.credentials = new AWS.CognitoIdentityCredentials({
//     IdentityPoolId: 'us-east-1:1da1482f-963e-4418-b103-c9d0393187e1',
// });

setTimeout(function() {
	if(cognito_token=="" || AWS.config.credentials.sessionToken==""){

		
		var appCilentId = 'Enter App client ID';
		var callbackUrl = 'https://s3.amazonaws.com/chatbot-devmahida/index.html';
		var domainName = 'https://mahida.auth.us-east-1.amazoncognito.com';


  redirectWebsite = domainName + '/login?response_type=token&client_id=' + appCilentId + '&redirect_uri=' + callbackUrl ;

  location.href = redirectWebsite;

  console.log(redirectWebsite);


}
}, 2000);



function sendMessageToApi(){


  var inputText = document.getElementById('user-input-message').value.trim().toLowerCase();

  document.getElementById('user-input-message').value = "";

  if(inputText == "") {
    alert("Please enter some text");
    return false;
  }else {

    chatHistory.push('<b><color = "red">User:</color> </b>' + inputText);

    document.getElementById('bot-response').innerHTML = "";

    chatHistory.forEach((element) => {
      document.getElementById('bot-response').innerHTML += "<p>" + element + "</p>";
    });

    receiveMessageFromApi(inputText);
    return false;
  }

}

function receiveMessageFromApi(inputText){

	  return AWS.config.credentials.getPromise()
  .then(()=>{


    console.log('Successfully logged!');

    apigClient = apigClientFactory.newClient({
      accessKey: AWS.config.credentials.accessKeyId,
      secretKey: AWS.config.credentials.secretAccessKey,
      sessionToken: AWS.config.credentials.sessionToken
    });

    var params = {};
    var body = {
      "message":inputText,
      "identityID":AWS.config.credentials._identityId
    };

    var additionalParams = {
      headers: {
        "x-api-key": "your API key",
      },
      queryParams: {}
    };
    return apigClient.chatbotPost(params,body,additionalParams);
 

  })
  .then((result) =>{


      chatHistory.push('<b><color = "Cyan">Bot:</color> </b>' + JSON.stringify(result.data.message));

      document.getElementById('bot-response').innerHTML = "";
      chatHistory.forEach((element) => {
        document.getElementById('bot-response').innerHTML += "<p>" +element + "</p>";
      });
  
  })
  .catch((err) =>{
    console.log(err);
  });

}

