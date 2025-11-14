# Leaflet to LinkedIn Article Workflow

## Executive Summary

**YES, this is absolutely feasible!** You can create a workflow where pressing a button triggers an AWS Lambda function to:
1. Fetch a Leaflet document from your ATProto PDS
2. Format it for LinkedIn
3. Either post directly via LinkedIn API OR return formatted text for manual posting

## Architecture Overview

```
[Leaflet Document in PDS]
    ↓
[Trigger Button] → [AWS Lambda Function] → [LinkedIn]
    ↓                     ↓
[Web UI/App]      [ATProto API Client]
                         ↓
                  [Format Converter]
                         ↓
                  Option A: LinkedIn API (automated posting)
                  Option B: Return formatted text (manual copy-paste)
```

## Key Components

### 1. Leaflet Document Structure

Leaflet documents are stored as ATProto records with the following schema:

**Record Type**: `pub.leaflet.document`

**Required Fields**:
- `title` - String (max 1280 chars, 128 graphemes)
- `author` - AT identifier
- `publication` - AT-URI format
- `pages` - Array of page objects (linearDocument or canvas types)

**Optional Fields**:
- `description` - String (max 3000 chars, 300 graphemes)
- `publishedAt` - Datetime
- `postRef` - Strong reference to AT protocol repository object

### 2. Accessing Documents from ATProto PDS

#### Authentication
Use OAuth 2.0 for ATProto authentication to access your PDS.

#### API Endpoints

**List Documents**:
```
GET https://[your-pds-host]/xrpc/com.atproto.repo.listRecords
?repo=[your-did]
&collection=pub.leaflet.document
```

**Get Specific Document**:
```
GET https://[your-pds-host]/xrpc/com.atproto.repo.getRecord
?repo=[your-did]
&collection=pub.leaflet.document
&rkey=[record-key]
```

**Response Example**:
```json
{
  "uri": "at://did:plc:xxx/pub.leaflet.document/xxx",
  "cid": "xxx",
  "value": {
    "title": "My Article Title",
    "author": "did:plc:xxx",
    "publication": "at://did:plc:xxx/pub.leaflet.publication/xxx",
    "pages": [...],
    "description": "Article description",
    "publishedAt": "2025-11-14T12:00:00Z"
  }
}
```

### 3. LinkedIn Integration

#### Important Limitation
LinkedIn's current API **does NOT support creating native LinkedIn Articles** (the long-form blogging platform). However, you have two viable options:

#### Option A: LinkedIn Posts API (Recommended)
Create a LinkedIn post with article-like content that appears in your feed.

**Endpoint**: `POST https://api.linkedin.com/rest/posts`

**Authentication**: OAuth 2.0 with `w_member_social` scope

**Required Headers**:
```
Authorization: Bearer {ACCESS_TOKEN}
Linkedin-Version: 202502
X-Restli-Protocol-Version: 2.0.0
Content-Type: application/json
```

**Request Body**:
```json
{
  "author": "urn:li:person:{PERSON_ID}",
  "commentary": "Check out my latest article: [Title]\n\n[Formatted content]",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED",
    "targetEntities": [],
    "thirdPartyDistributionChannels": []
  },
  "lifecycleState": "PUBLISHED",
  "isReshareDisabledByAuthor": false
}
```

**Limitations**:
- Character limit for commentary (3000 characters for posts)
- Limited formatting options
- Appears as a post, not a native article

#### Option B: Formatted Text for Manual Posting
Generate LinkedIn-formatted markdown/text that you can copy-paste into LinkedIn's article editor.

**Advantages**:
- Full access to LinkedIn's native article formatting
- No API restrictions
- Better SEO and discoverability
- Proper article URL (linkedin.com/pulse/article-slug)

**Format Example**:
```
Title: [Article Title]

[Formatted paragraphs with proper spacing]

Use LinkedIn's editor for:
- Headers (## for H2, ### for H3)
- Bold text
- Italic text
- Bullet points
- Links
- Images (upload separately)
```

## Implementation Guide

### Phase 1: AWS Lambda Function Setup

#### 1.1 Create Lambda Function

```javascript
// lambda/leaflet-to-linkedin/index.js

const { BskyAgent } = require('@atproto/api');

exports.handler = async (event) => {
  try {
    // Parse request
    const { documentUri, linkedinOption } = JSON.parse(event.body);

    // Step 1: Fetch from ATProto PDS
    const agent = new BskyAgent({ service: process.env.PDS_URL });
    await agent.login({
      identifier: process.env.ATPROTO_IDENTIFIER,
      password: process.env.ATPROTO_PASSWORD
    });

    const document = await fetchLeafletDocument(agent, documentUri);

    // Step 2: Convert to LinkedIn format
    const formattedContent = convertToLinkedInFormat(document);

    // Step 3: Either post to LinkedIn or return formatted text
    let result;
    if (linkedinOption === 'api') {
      result = await postToLinkedIn(formattedContent);
    } else {
      result = { formattedText: formattedContent };
    }

    return {
      statusCode: 200,
      body: JSON.stringify(result)
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};

async function fetchLeafletDocument(agent, documentUri) {
  // Parse AT-URI: at://did:plc:xxx/pub.leaflet.document/rkey
  const [, , did, collection, rkey] = documentUri.split('/');

  const response = await agent.api.com.atproto.repo.getRecord({
    repo: did,
    collection: 'pub.leaflet.document',
    rkey: rkey
  });

  return response.data.value;
}

function convertToLinkedInFormat(document) {
  let content = '';

  // Add title
  content += `# ${document.title}\n\n`;

  // Add description if available
  if (document.description) {
    content += `${document.description}\n\n`;
  }

  // Process pages
  for (const page of document.pages) {
    if (page.linearDocument) {
      content += processLinearPage(page.linearDocument);
    }
    // Add canvas page handling if needed
  }

  return content;
}

function processLinearPage(page) {
  let text = '';

  // This will depend on the actual structure of linearDocument pages
  // You'll need to parse the blocks within each page
  // Common blocks might include: paragraph, heading, list, image, etc.

  if (page.blocks) {
    for (const block of page.blocks) {
      text += processBlock(block);
    }
  }

  return text;
}

function processBlock(block) {
  // Handle different block types
  // This is a simplified example - actual implementation will depend on Leaflet's block structure

  if (block.paragraph) {
    return `${block.paragraph.text}\n\n`;
  }

  if (block.heading) {
    const level = '#'.repeat(block.heading.level);
    return `${level} ${block.heading.text}\n\n`;
  }

  if (block.list) {
    return block.list.items.map(item => `- ${item}`).join('\n') + '\n\n';
  }

  return '';
}

async function postToLinkedIn(content) {
  const axios = require('axios');

  const response = await axios.post(
    'https://api.linkedin.com/rest/posts',
    {
      author: `urn:li:person:${process.env.LINKEDIN_PERSON_ID}`,
      commentary: content.substring(0, 3000), // LinkedIn limit
      visibility: 'PUBLIC',
      distribution: {
        feedDistribution: 'MAIN_FEED'
      },
      lifecycleState: 'PUBLISHED'
    },
    {
      headers: {
        'Authorization': `Bearer ${process.env.LINKEDIN_ACCESS_TOKEN}`,
        'Linkedin-Version': '202502',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
      }
    }
  );

  return { postId: response.data.id, url: response.headers['x-linkedin-id'] };
}
```

#### 1.2 Environment Variables

Configure in AWS Lambda:
```
PDS_URL=https://your-pds-host.com
ATPROTO_IDENTIFIER=your-handle.bsky.social
ATPROTO_PASSWORD=your-app-password
LINKEDIN_ACCESS_TOKEN=your-linkedin-token
LINKEDIN_PERSON_ID=your-person-id
```

#### 1.3 Lambda Configuration

- **Runtime**: Node.js 18.x or later
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Layers**: Install `@atproto/api` and `axios` via Lambda layers or package with function

### Phase 2: Trigger Button Implementation

#### Option 1: Web Application

```html
<!-- leaflet-linkedin-button.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Leaflet to LinkedIn</title>
</head>
<body>
  <h1>Convert Leaflet Document to LinkedIn</h1>

  <form id="convertForm">
    <label for="documentUri">Leaflet Document URI:</label>
    <input
      type="text"
      id="documentUri"
      placeholder="at://did:plc:xxx/pub.leaflet.document/xxx"
      style="width: 500px"
    />

    <br><br>

    <label>LinkedIn Option:</label>
    <input type="radio" id="optionApi" name="linkedinOption" value="api" checked>
    <label for="optionApi">Post via API</label>

    <input type="radio" id="optionText" name="linkedinOption" value="text">
    <label for="optionText">Get formatted text</label>

    <br><br>

    <button type="submit">Convert & Post</button>
  </form>

  <div id="result" style="margin-top: 20px; display: none;">
    <h2>Result:</h2>
    <pre id="resultText"></pre>
  </div>

  <script>
    document.getElementById('convertForm').addEventListener('submit', async (e) => {
      e.preventDefault();

      const documentUri = document.getElementById('documentUri').value;
      const linkedinOption = document.querySelector('input[name="linkedinOption"]:checked').value;

      try {
        const response = await fetch('YOUR_LAMBDA_URL', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ documentUri, linkedinOption })
        });

        const result = await response.json();

        document.getElementById('result').style.display = 'block';
        document.getElementById('resultText').textContent = JSON.stringify(result, null, 2);

        if (linkedinOption === 'text' && result.formattedText) {
          // Copy to clipboard
          navigator.clipboard.writeText(result.formattedText);
          alert('Formatted text copied to clipboard! Paste into LinkedIn.');
        } else if (linkedinOption === 'api' && result.postId) {
          alert('Successfully posted to LinkedIn!');
        }

      } catch (error) {
        alert('Error: ' + error.message);
      }
    });
  </script>
</body>
</html>
```

#### Option 2: Browser Extension

Create a Chrome/Firefox extension that adds a "Share to LinkedIn" button directly on Leaflet.pub pages.

**manifest.json**:
```json
{
  "manifest_version": 3,
  "name": "Leaflet to LinkedIn",
  "version": "1.0",
  "permissions": ["activeTab", "storage"],
  "content_scripts": [{
    "matches": ["https://leaflet.pub/*"],
    "js": ["content.js"]
  }],
  "background": {
    "service_worker": "background.js"
  }
}
```

#### Option 3: Slack/Discord Bot

Create a bot command like `/leaflet-to-linkedin [document-uri]` that triggers the Lambda function.

### Phase 3: LinkedIn OAuth Setup

#### 3.1 Create LinkedIn App

1. Go to https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in app details
4. Under "Products", add "Share on LinkedIn"
5. Under "Auth", add redirect URL

#### 3.2 OAuth Flow

```javascript
// Get authorization code
const authUrl = `https://www.linkedin.com/oauth/v2/authorization?` +
  `response_type=code&` +
  `client_id=${CLIENT_ID}&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `scope=w_member_social`;

// Exchange code for token
const tokenResponse = await axios.post(
  'https://www.linkedin.com/oauth/v2/accessToken',
  new URLSearchParams({
    grant_type: 'authorization_code',
    code: authCode,
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    redirect_uri: REDIRECT_URI
  })
);

const accessToken = tokenResponse.data.access_token;
```

## Cost Estimates

### AWS Lambda
- **Free Tier**: 1M requests/month, 400,000 GB-seconds
- **Cost per invocation**: ~$0.0000002 (practically free for personal use)

### LinkedIn API
- **Cost**: Free for personal use
- **Rate Limits**: 500 requests per app per day

## Recommended Approach

Based on research, I recommend **Option B: Formatted Text** for the following reasons:

### Why Formatted Text is Better

1. **Native Article Experience**: LinkedIn's native article editor provides:
   - Better formatting options
   - SEO benefits (articles appear at linkedin.com/pulse/...)
   - Better discovery (LinkedIn's article recommendation algorithm)
   - Professional appearance

2. **No API Limitations**:
   - No character limits (articles can be 40,000+ characters)
   - Full formatting support
   - Image embedding
   - No rate limiting concerns

3. **Simpler Implementation**:
   - No LinkedIn OAuth flow needed
   - No token management
   - No API version updates

### Hybrid Approach (Best of Both Worlds)

1. **Lambda returns formatted text** with a "Copy to Clipboard" button
2. **Also create a LinkedIn post** (via API) that says: "I just published a new article on LinkedIn" with a link
3. **User pastes** the formatted text into LinkedIn's article editor

## Next Steps

1. **Explore Leaflet's Page Structure**: Investigate the actual structure of `linearDocument` and `canvas` pages to build accurate parsers
2. **Build Parser**: Create converters for different Leaflet block types (paragraph, heading, list, image, etc.)
3. **Set Up Lambda**: Deploy the Lambda function with proper error handling
4. **Create UI**: Build your preferred trigger mechanism (web app, extension, or bot)
5. **Test**: Start with Option B (formatted text) for simplicity
6. **Iterate**: Add API posting if desired later

## Code Repository Structure

```
leaflet-to-linkedin/
├── lambda/
│   ├── index.js              # Main Lambda handler
│   ├── atproto-client.js     # ATProto PDS client
│   ├── linkedin-client.js    # LinkedIn API client
│   ├── formatters/
│   │   ├── markdown.js       # Convert to markdown
│   │   └── html.js           # Convert to HTML
│   └── package.json
├── frontend/
│   ├── index.html            # Web UI
│   └── app.js
├── extension/                 # Optional browser extension
│   ├── manifest.json
│   ├── content.js
│   └── background.js
└── README.md
```

## Security Considerations

1. **Never commit tokens**: Use AWS Systems Manager Parameter Store or Secrets Manager
2. **Validate inputs**: Sanitize document URIs to prevent injection
3. **Rate limiting**: Implement throttling to avoid API abuse
4. **CORS**: Configure proper CORS headers on Lambda
5. **Authentication**: Add authentication to your trigger button to prevent unauthorized use

## Additional Features to Consider

1. **Preview**: Show formatted LinkedIn content before posting
2. **Template Selection**: Different formatting styles for different audiences
3. **Image Handling**: Download images from PDS and upload to LinkedIn
4. **Scheduling**: Queue posts for later publishing
5. **Analytics**: Track which documents get converted most
6. **Batch Processing**: Convert multiple documents at once

## Conclusion

This workflow is **100% feasible** and can be implemented in a weekend. The recommended approach is:

1. Start with **Option B (formatted text)** for maximum flexibility
2. Build a simple web UI with a button
3. Use AWS Lambda for the conversion logic
4. Manually paste into LinkedIn's article editor

Once this works, you can iterate to add API posting, browser extensions, or other automation features.

The beauty of this architecture is that it's:
- **Scalable**: Lambda handles any traffic
- **Cost-effective**: Nearly free for personal use
- **Flexible**: Easy to add new formats or destinations
- **Simple**: No complex infrastructure needed
