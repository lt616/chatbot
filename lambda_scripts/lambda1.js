'use strict';


function elicitSlot(sessionAttributes, intentName, slots, slotToElicit, message) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'ElicitSlot',
            intentName,
            slots,
            slotToElicit,
            message,
        },
    };
}

function delegate(sessionAttributes, slots) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'Delegate',
            slots,
        },
    };
}

// Close dialog with the customer, reporting fulfillmentState of Failed or Fulfilled ("Thanks, your pizza will arrive in 20 minutes")
function close(sessionAttributes, fulfillmentState, message) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'Close',
            fulfillmentState,
            message,
        },
    };
}



// --------------- Events -----------------------
 
function dispatch(intentRequest, callback) {
    console.log(`request received for userId=${intentRequest.userId}, intentName=${intentRequest.currentIntent.name}`);
    const sessionAttributes = intentRequest.sessionAttributes;
    const intentName = intentRequest.currentIntent.name;
    // const intentName = "FindRestaurants";
    if (intentName === 'GreetingIntent') {
        callback(close(sessionAttributes, 'Fulfilled',
        {'contentType': 'PlainText', 'content': `Hello! How can I help?`}));
    }
    if (intentName === 'ThankYouIntent') {
        callback(close(sessionAttributes, 'Fulfilled',
        {'contentType': 'PlainText', 'content': `You are welcome!`}));
    }
    if (intentName === 'FindRestaurants') {
        const slots = intentRequest.currentIntent.slots;
        const MealLocation = slots.MealLocation;
        const MealCuisine = slots.MealCuisine;
        const MealDate = slots.MealDate;
        const MealTime = slots.MealTime;
        const ClientPhoneNum = slots.ClientPhoneNum;
        const ClientNum = slots.ClientNum;
        callback(close(sessionAttributes, 'Fulfilled',
        {'contentType': 'PlainText', 'content': `Ok, I've got your information. Don't worry. We will give recommendations to you ASAP!`}));
        // Load the AWS SDK for Node.js
        var AWS = require('aws-sdk');
        // Set the region 
        AWS.config.update({region: 'us-west-2'});
        
        // Create an SQS service object
        var sqs = new AWS.SQS({apiVersion: '2012-11-05'});
        
        var data = {
            'MealLocation': MealLocation, 
            'MealCuisine': MealCuisine, 
            'MealDate': MealDate, 
            'MealTime': MealTime, 
            'ClientPhoneNum': ClientPhoneNum, 
            'ClientNum': ClientNum
        }
        
        
        
        var params = {
         DelaySeconds: 0,
         MessageAttributes: {
         },
         MessageBody: JSON.stringify(data),
         QueueUrl: "https://sqs.us-west-2.amazonaws.com/219260801235/chatbot-sqs"
        };
        
        sqs.sendMessage(params, function(err, data) {
            console.log("match");
          if (err) {
            console.log("Error", err);
          } else {
            console.log("Success", data.MessageId);
          }
        });
        
    }
}
 
// --------------- Main handler -----------------------
 
// Route the incoming request based on intent.
// The JSON body of the request is provided in the event slot.
exports.handler = (event, context, callback) => {
    try {
        console.log(`event.bot.name=${event.bot.name}`);
        dispatch(event,
            (response) => {
                callback(null, response);
            });
    } catch (err) {
        callback(err);
    }
};
 
