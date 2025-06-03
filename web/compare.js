const express = require('express');
const http = require('http');
const cors = require('cors');
const path = require('path');
const app = express();

app.use(cors({
  origin: '*',
  methods: ['GET', 'POST']
}));

app.get('/', (req, res) => {
  const filePath = path.join(__dirname, 'compare.html');
  res.sendFile(filePath);
});

const server = http.createServer(app);
const io = require("socket.io")(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  }
});

app.use(cors({ origin: "*" }))

io.on('connection', (socket) => {
  console.log('connection now...')
  socket.on('message', (data) => {
    // console.log('Data');
    // console.log(data);
    io.emit('message', data)
  });

  socket.on('userprompted', (data) => {
    console.log('Data');
    console.log(data);
    io.emit('userprompted', data)
  });


  socket.on('disconnect', () => {
    console.log('A client disconnected');
  });
});

const port = 9000;
server.listen(port, () => {
  console.log(`Server started on port ${port}`);
});