const Client = require('ssh2').Client;

exports.handler = async function (event, context) {
  return new Promise((resolve, reject) => {
    const conn = new Client();

    // Load credentials from environment variables
    const host = process.env.SSH_HOST;
    const username = process.env.SSH_USERNAME;
    const password = process.env.SSH_PASSWORD;

    conn
      .on('ready', () => {
        conn.exec('uptime', (err, stream) => {
          if (err) {
            conn.end();
            return reject({
              statusCode: 500,
              body: JSON.stringify({ error: err.message }),
            });
          }

          let data = '';
          stream
            .on('close', (code, signal) => {
              conn.end();

              // Determine if the server is online based on the output
              const isOnline = data.includes('load average');

              resolve({
                statusCode: 200,
                body: JSON.stringify({ status: isOnline ? 'Online' : 'Offline' }),
              });
            })
            .on('data', (chunk) => {
              data += chunk;
            })
            .stderr.on('data', (chunk) => {
              console.error('STDERR:', chunk.toString());
            });
        });
      })
      .on('error', (err) => {
        reject({
          statusCode: 500,
          body: JSON.stringify({ error: 'Connection error: ' + err.message }),
        });
      })
      .connect({
        host,
        port: 22,
        username,
        password,
      });
  });
};
