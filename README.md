<p align="center"> <img src="Project Elements/Simple_Email_Beacon.png"/> </p>

<hr>
<br/>

```BSC MEV``` is a program that aimed to profit through the exploitation of block transaction fees.

## Use Case
Your first question is most likely "well if you have an infinite money printer why would you share it knowing the blockchain would become saturated and in turn break program?" well frankly, it does not exactly work as intended. 

```
- IP Address
- Date and Time
- Country
- City
- Timezone
```


## Installation

Use the package manager npm to install the following packages

```bash
npm install express
npm install express-ip
```

## Usage
This project will be a working UI within the next few weeks but in the meantime, the tool can be used with the following commands. To follow our progress please follow our repo: https://github.com/cszach/email-beacon-frontend
```JavaScript
// Initialize express web client on a local host, port 3000
node main.js
```

```curl
// Generate hash to insert into an email
curl --insecure -H "Content-type: application/json" 'http://127.0.0.1:3000/generateHash'
```

```
// Periodically send get requests to the following URL to get the mail status
curl --insecure -H "Content-type: application/json" 'http://127.0.0.1:3000/emailBeaconStatus?hash=<YOUR_GENERATED_HASH>'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
