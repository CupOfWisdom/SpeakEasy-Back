// src/api/routes.js
import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

const router = express.Router();
const upload = multer({ dest: 'src/api/uploads/' });

// Endpoint to upload JSON files
router.post('/upload-json', upload.single('file'), (req, res) => {
    const tempPath = req.file.path;
    const targetPath = path.join(process.cwd(), 'src', 'public', 'emotion_data.json');

    if (path.extname(req.file.originalname).toLowerCase() === '.json') {
        fs.rename(tempPath, targetPath, err => {
            if (err) return res.sendStatus(500);

            res.status(200).json({ message: 'JSON file uploaded successfully', filename: req.file.originalname });
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
    const filePath = path.join(process.cwd(), 'src', 'api', 'public', 'emotion_data.json');
    res.download(filePath, 'emotion_data.json', (err) => {
        if (err) {
            res.status(500).send('Error downloading the file');
        }
    });
});

// Endpoint to upload video files and process them
router.post('/upload-video', upload.single('file'), (req, res) => {
    const tempPath = req.file.path;
    const targetPath = path.join(process.cwd(), 'src', 'api', 'public', 'uploaded_video.mp4');

    if (req.file.mimetype.startsWith('video/')) {
        fs.rename(tempPath, targetPath, err => {
            if (err) {
                console.error('Error:', err);
                return res.status(500).json({ message: 'Error renaming the file', err });
            }

            // Return response immediately
            res.status(200).json({ message: 'Video file uploaded successfully, processing started', filename: req.file.originalname });

            // Process the video asynchronously
            exec(`TF_ENABLE_ONEDNN_OPTS=0 python3 ./src/model/process_video.py "${targetPath}"`, (error, stdout, stderr) => {
                if (error) {
                    console.error('Execution error:', error);
                    return;
                }

                console.log('stdout:', stdout);
                console.error('stderr:', stderr);

                // Delete the video file after processing
                fs.unlink(targetPath, (unlinkError) => {
                    if (unlinkError) {
                        console.error('Error deleting the video file:', unlinkError);
                    }
                });
            });
        });
    } else {
        fs.unlink(tempPath, err => {
            if (err) {
                console.error('Error:', err);
                return res.status(500).json({ message: 'Error deleting the temp file', err });
            }

            res.status(400).json({ message: 'Only video files are allowed!' });
        });
    }
});

// Endpoint to download the video file
router.get('/download-video', (req, res) => {
    const filePath = path.join(process.cwd(), 'src', 'api', 'public', 'uploaded_video.mp4');
    res.download(filePath, 'uploaded_video.mp4', (err) => {
        if (err) {
            res.status(500).send('Error downloading the file');
        }
    });
});

router.get('/status', (req, res) => {
    const outputJsonPath = path.join(process.cwd(), 'src', 'api', 'public', 'json', 'emotion_data.json');

    fs.access(outputJsonPath, fs.constants.F_OK, (err) => {
        if (err) {
            return res.status(200).json({ status: 'processing' });
        }
        res.status(200).json({ status: 'completed' });
    });
});

export default router;
