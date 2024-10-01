const crypto = require('crypto');

exports.handler = async (event) => {
  try {
    const BOT_TOKEN = process.env.BOT_TOKEN;

    // Get initData from query parameters
    const { initData } = event.queryStringParameters;

    if (!initData) {
      console.error('No initData provided');
      return {
        statusCode: 400,
        body: JSON.stringify({ ok: false, error: 'No initData provided' }),
      };
    }

    // Create a secret key using the bot token
    const secretKey = crypto.createHash('sha256').update(BOT_TOKEN).digest();

    // Parse initData to extract the hash parameter
    const params = new URLSearchParams(initData);
    const hash = params.get('hash');

    if (!hash) {
      console.error('Hash not found in initData');
      return {
        statusCode: 400,
        body: JSON.stringify({ ok: false, error: 'Hash not found in initData' }),
      };
    }

    // Remove the hash parameter from initData
    params.delete('hash');
    const dataCheckString = Array.from(params.entries())
      .sort()
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');

    // Compute the HMAC-SHA256 hash
    const hmac = crypto
      .createHmac('sha256', secretKey)
      .update(dataCheckString)
      .digest('hex');

    if (hmac === hash) {
      return {
        statusCode: 200,
        body: JSON.stringify({ ok: true }),
      };
    } else {
      console.error('Invalid hash:', { expected: hmac, received: hash });
      return {
        statusCode: 401,
        body: JSON.stringify({ ok: false, error: 'Invalid hash' }),
      };
    }
  } catch (error) {
    console.error('Error in verifyAuth function:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ ok: false, error: 'Server error' }),
    };
  }
};
// After computing hmac
console.log('Computed HMAC:', hmac);
console.log('Received hash:', hash);
console.log('Data Check String:', dataCheckString);
