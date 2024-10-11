// src/pages/MyKeys.tsx
import React, { useEffect, useState } from 'react';
import { Box, Typography, List, ListItem, ListItemText, ListItemIcon, IconButton, Divider } from '@mui/material';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { CopyToClipboard } from 'react-copy-to-clipboard';

const MyKeys: React.FC = () => {
  const [keys, setKeys] = useState<string[]>([]);

  useEffect(() => {
    // TODO: Fetch the user's VPN keys from your API
    // Mock data for now
    setKeys([
      'abc123-def456-ghi789',
      'jkl012-mno345-pqr678',
      'stu901-vwx234-yza567',
    ]);
  }, []);

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        My Keys
      </Typography>
      <List>
        {keys.map((key, index) => (
          <React.Fragment key={index}>
            <ListItem
              secondaryAction={
                <CopyToClipboard text={key}>
                  <IconButton edge="end" aria-label="copy">
                    <ContentCopyIcon />
                  </IconButton>
                </CopyToClipboard>
              }
            >
              <ListItemIcon>
                <VpnKeyIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary={`Key ${index + 1}`} secondary={key} />
            </ListItem>
            {index < keys.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
};

export default MyKeys;
