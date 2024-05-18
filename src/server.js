// src/server.js
import express from 'express';
import path from 'path';
import apiRoutes from './api/routes.js';

const app = express();
const port = 3000;

// Serve the index.html file at the root endpoint
app.get('/', (req, res) => {
    res.sendFile(path.join(process.cwd(), 'src', 'public', 'index.html'));
});

app.use('/api', apiRoutes);
app.use(express.static('src/public'));

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
