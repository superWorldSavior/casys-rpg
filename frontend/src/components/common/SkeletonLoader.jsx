import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Skeleton,
  Box,
  CardActions,
} from '@mui/material';

const SkeletonLoader = ({ count = 6 }) => (
  <Grid container spacing={3}>
    {[...Array(count)].map((_, index) => (
      <Grid item xs={12} sm={6} md={4} key={`skeleton-${index}`}>
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Skeleton
            variant="rectangular"
            height={200}
            animation="wave"
            sx={{ m: 1 }}
          />
          <CardContent sx={{ flexGrow: 1 }}>
            <Skeleton variant="text" height={32} width="80%" sx={{ mb: 1 }} />
            <Skeleton variant="text" height={24} width="60%" sx={{ mb: 2 }} />
            <Skeleton variant="rounded" height={24} width="40%" sx={{ mb: 1 }} />
            <Box sx={{ mb: 2 }}>
              <Skeleton variant="rounded" height={32} width="100%" />
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Skeleton variant="rounded" height={32} width="30%" />
              <Skeleton variant="rounded" height={32} width="30%" />
              <Skeleton variant="rounded" height={32} width="30%" />
            </Box>
          </CardContent>
          <CardActions sx={{ p: 2, justifyContent: 'space-between' }}>
            <Skeleton variant="rounded" width={100} height={36} />
            <Skeleton variant="rounded" width={100} height={36} />
          </CardActions>
        </Card>
      </Grid>
    ))}
  </Grid>
);

export default SkeletonLoader;
