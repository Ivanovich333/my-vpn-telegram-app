const crypto = require('crypto');

exports.handler = async (event) => {
  const BOT_TOKEN = process.env.BOT_TOKEN; // Set this in your Netlify environment variables
  const urlParams = new URLSearchParams(event.queryStringParameters);
  const authData = Object.fromEntries(urlParams.entries());

  const { hash, ...dataCheck } = authData;
  const checkString = Object.keys(dataCheck)
    .sort()
    .map((key) => `${key}=${dataCheck[key]}`)
    .join('\n');

  const secretKey = crypto
    .createHash('sha256')
    .update(BOT_TOKEN)
    .digest();

  const hmac = crypto
    .createHmac('sha256', secretKey)
    .update(checkString)
    .digest('hex');

  if (hmac === hash) {
    return {
      statusCode: 200,
      body: JSON.stringify({ ok: true }),
    };
  } else {
    return {
      statusCode: 401,
      body: JSON.stringify({ ok: false, error: 'Invalid hash' }),
    };
  }
};
