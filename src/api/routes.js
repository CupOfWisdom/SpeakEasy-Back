// src/api/upload.js
import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';

const router = express.Router();
const upload = multer({ dest: 'uploads/' });

// Endpoint to upload JSON files
router.post('/upload', upload.single('file'), (req, res) => {
    const tempPath = req.file.path;
    const targetPath = path.join(process.cwd(), 'src', 'public', 'emotion_data.json');

    if (path.extname(req.file.originalname).toLowerCase() === '.json') {
        fs.rename(tempPath, targetPath, err => {
            if (err) return res.sendStatus(500);

            res.status(200).json({ message: 'File uploaded successfully', filename: req.file.originalname });
        });
    } else {
        fs.unlink(tempPath, err => {
            if (err) return res.sendStatus(500);

            res.status(400).json({ message: 'Only JSON files are allowed!' });
        });
    }
});

// Endpoint to download the JSON file
router.get('/download-json', (req, res) => {
    const filePath = path.join(process.cwd(), 'src', 'public', 'emotion_data.json');
    res.download(filePath, 'emotion_data.json', (err) => {
        if (err) {
            res.status(500).send('Error downloading the file');
        }
    });
});

export default router;
