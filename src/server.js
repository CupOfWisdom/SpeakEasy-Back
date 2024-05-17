// src/server.js
import express from 'express';
import apiRoutes from './api/routes.js';
import path from 'path';

const app = express();
const port = 3000;

app.use('/api', apiRoutes);
app.use(express.static('src/public'));

app.get('/', (req, res) => {
    res.sendFile(path.join(process.cwd(), 'src', 'public', 'index.html'));
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
