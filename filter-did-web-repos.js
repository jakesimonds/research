#!/usr/bin/env node

// Script to fetch repos from a PDS and filter for did:web DIDs
// Usage: node filter-did-web-repos.js [pds-hostname]

const pdsHost = process.argv[2] || 'bsky.network';
const url = `https://${pdsHost}/xrpc/com.atproto.sync.listRepos`;

console.log(`Fetching repos from: ${url}\n`);

async function fetchAndFilterRepos() {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    console.log(`Total repos fetched: ${data.repos ? data.repos.length : 0}`);

    // Filter for did:web
    const didWebAccounts = data.repos.filter(repo =>
      repo.did.startsWith('did:web:')
    );

    console.log(`\nDIDs using did:web: ${didWebAccounts.length}\n`);

    if (didWebAccounts.length === 0) {
      console.log('No did:web repos found.');
    } else {
      console.log('List of did:web DIDs:\n');
      didWebAccounts.forEach((repo, index) => {
        console.log(`${index + 1}. ${repo.did}`);
        if (repo.head) console.log(`   Head: ${repo.head}`);
        if (repo.rev) console.log(`   Rev: ${repo.rev}`);
        console.log('');
      });

      // Save to file
      const fs = require('fs');
      const outputFile = 'did-web-repos.json';
      fs.writeFileSync(outputFile, JSON.stringify(didWebAccounts, null, 2));
      console.log(`\nResults saved to: ${outputFile}`);
    }

  } catch (error) {
    console.error('Error:', error.message);
    if (error.cause) {
      console.error('Cause:', error.cause);
    }
  }
}

fetchAndFilterRepos();
