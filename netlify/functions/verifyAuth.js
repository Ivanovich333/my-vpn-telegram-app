const crypto = require('crypto');

exports.handler = async (event) => {
  try {
    const BOT_TOKEN = process.env.BOT_TOKEN;

    if (!BOT_TOKEN) {
      console.error('BOT_TOKEN is not set');
      return {
        statusCode: 500,
        body: JSON.stringify({ ok: false, error: 'Server configuration error: BOT_TOKEN not set' }),
      };
    } else {
      console.log('BOT_TOKEN is set');
      // For security reasons, do not log the actual BOT_TOKEN value
    }

    // The rest of your function...
    // Get initData from query parameters
    const { initData } = event.queryStringParameters || {};

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

    // Remove the hash parameter from params
    params.delete('hash');

    // Create data check string
    const dataCheckString = Array.from(params.entries())
      .sort()
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');

    console.log('Data Check String:', dataCheckString);

    // Compute the HMAC-SHA256 hash
    const hmac = crypto
      .createHmac('sha256', secretKey)
      .update(dataCheckString)
      .digest('hex');

    console.log('Computed HMAC:', hmac);
    console.log('Received hash:', hash);

    if (hmac === hash) {
      console.log('Authentication successful');
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
