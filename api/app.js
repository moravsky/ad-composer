const express = require('express');
const OpenAI = require('openai');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 8080;
const cors = require('cors');

app.use(express.json());
app.use(cors());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_DATABASE,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

app.get('/api/account-names', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        key AS account_name
      FROM 
        target_accounts, 
        jsonb_each(data)
      WHERE 
        key != 'meta'
    `);

    // Extract just the account names
    const accountNames = result.rows.map(row => row.account_name);

    res.json(accountNames);
  } catch (err) {
    console.error('Error retrieving account names:', err);
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/personalize', async (req, res) => {
  try {
    const { client, texts } = req.body;

    // Validate input
    if (!client || !texts || !Array.isArray(texts) || texts.length === 0) {
      return res.status(400).json({ error: 'Invalid input' });
    }

    // Construct personalization prompt
    const prompt = `
      You are a marketing expert specializing in personalized content creation.
      
      Client: ${client}
      
      Personalize the following texts to make them more appealing and relevant to ${client}:
      
      ${texts.map((text, index) => `Text ${index + 1}: ${text}`).join('\n\n')}
      
      Please return ONLY the personalized text for each input, without any additional explanation.
    `;

    // Call OpenAI API
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content: "You are a helpful marketing expert specializing in content personalization. Return only the personalized text."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      max_tokens: 1000,
      temperature: 0.7
    });

    // Get the full content
    const fullContent = completion.choices[0].message.content;
    console.log('Full OpenAI Response:', fullContent); // Add this for debugging

    // Extract personalized texts
    const personalizedTexts = texts.map((_, index) => {
      const lines = fullContent.split('\n');
      const targetLine = lines.find(line => line.startsWith(`Text ${index + 1}:`));

      if (targetLine) {
        // Remove the "Text X:" prefix and trim
        return targetLine.replace(`Text ${index + 1}:`, '').trim();
      }

      return '';
    });

    res.json({
      client: client,
      originalTexts: texts,
      personalizedContent: personalizedTexts
    });

  } catch (error) {
    console.error('Personalization error:', error);
    res.status(500).json({
      error: 'Failed to personalize content',
      details: error.message
    });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});