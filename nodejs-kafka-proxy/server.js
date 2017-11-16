const kafka = require('kafka-node')
const express = require('express')
const app = express()

const Producer = kafka.Producer
const client = new kafka.Client()
const producer = new Producer(client)

app.get('/', (req, res) => res.send('Kafka Proxy server!'))

app.all('/proxy', (req, res) => {
  res.send("Send message by POST /proxy/:topic")
})

app.all('/proxy/:topic', (req, res) => {
  const topic = req.params['topic'];
  const messages = JSON.stringify(req.method == 'POST' ? req.body : req.query);
  const payloads = [{ topic, messages }];
  console.log("===> Payload data: ", payloads);

  producer.send(payloads, function (err, data) {
      if (err) {
        return res.status(999).json({error: 1, message: err, topic, data})
      } else {
        console.log(data);
        res.json({error:0, message: 'success', topic, data})
      }
  });
})

producer.on('ready', function () {
  app.listen(3000, () => console.log('Example app listening on port 3000!'))
})
