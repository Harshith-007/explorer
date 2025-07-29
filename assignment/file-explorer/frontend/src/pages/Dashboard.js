import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiFolder, FiFile, FiDownload, FiTrash2, FiUpload, FiLogOut, FiPlus, FiFolderPlus } from 'react-icons/fi';
import { getFileTree, uploadFile, downloadFile, deleteFile, createFolder } from '../services/api';

const Dashboard = ({ user, onLogout }) => {
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  const fetchFiles = async (path = '') => {
    setLoading(true);
    setError('');
    
    try {
      const response = await getFileTree(path);
      setFiles(response.tree);
      setCurrentPath(response.current_path);
    } catch (error) {
      setError('Failed to load files');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const onDrop = async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      try {
        await uploadFile(file, currentPath);
        fetchFiles(currentPath);
      } catch (error) {
        setError(`Failed to upload ${file.name}`);
        console.error(error);
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const handleDownload = async (filePath) => {
    try {
      await downloadFile(filePath);
    } catch (error) {
      setError('Failed to download file');
      console.error(error);
    }
  };

  const handleDelete = async (filePath) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        await deleteFile(filePath);
        fetchFiles(currentPath);
      } catch (error) {
        setError('Failed to delete file');
        console.error(error);
      }
    }
  };

  const handleFolderClick = (folderPath) => {
    fetchFiles(folderPath);
  };

  const handleBackClick = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/');
    fetchFiles(parentPath);
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;
    
    try {
      await createFolder(newFolderName, currentPath);
      setNewFolderName('');
      setShowCreateFolder(false);
      fetchFiles(currentPath);
    } catch (error) {
      setError('Failed to create folder');
      console.error(error);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>File Explorer</h1>
        <div className="user-info">
          {user.picture && <img src={user.picture} alt={user.name} className="user-avatar" />}
          <span>{user.name}</span>
          <button onClick={onLogout} className="logout-btn">
            <FiLogOut />
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="file-explorer">
          <div className="toolbar">
            <div className="breadcrumb">
              <button onClick={() => fetchFiles('')}>Home</button>
              {currentPath && (
                <>
                  {currentPath.split('/').map((segment, index, array) => (
                    <span key={index}>
                      / 
                      {index < array.length - 1 ? (
                        <button onClick={() => fetchFiles(array.slice(0, index + 1).join('/'))}>
                          {segment}
                        </button>
                      ) : (
                        <span className="current-segment">{segment}</span>
                      )}
                    </span>
                  ))}
                </>
              )}
            </div>
            <div className="toolbar-actions">
              <button 
                onClick={() => setShowCreateFolder(true)} 
                className="create-folder-btn"
                title="Create Folder"
              >
                <FiFolderPlus />
              </button>
              {currentPath && (
                <button onClick={handleBackClick} className="back-btn">
                  Back
                </button>
              )}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          {showCreateFolder && (
            <div className="create-folder-modal">
              <div className="modal-content">
                <h3>Create New Folder</h3>
                <input
                  type="text"
                  placeholder="Folder name"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleCreateFolder()}
                />
                <div className="modal-actions">
                  <button onClick={handleCreateFolder}>Create</button>
                  <button onClick={() => {
                    setShowCreateFolder(false);
                    setNewFolderName('');
                  }}>Cancel</button>
                </div>
              </div>
            </div>
          )}

          <div 
            {...getRootProps()} 
            className={`upload-area ${isDragActive ? 'drag-active' : ''}`}
          >
            <input {...getInputProps()} />
            <FiUpload />
            <p>
              {isDragActive
                ? 'Drop files here...'
                : 'Drag & drop files here, or click to select files'
              }
            </p>
          </div>

          <div className="file-list">
            {loading ? (
              <div className="loading">Loading...</div>
            ) : (
              files.map((item, index) => (
                <div key={index} className="file-item">
                  <div 
                    className="file-info"
                    onClick={item.type === 'folder' ? () => handleFolderClick(item.path) : undefined}
                  >
                    {item.type === 'folder' ? <FiFolder /> : <FiFile />}
                    <span className="file-name">{item.name}</span>
                    <span className="file-size">
                      {item.type === 'file' && item.size && `${(item.size / 1024).toFixed(2)} KB`}
                    </span>
                    <span className="file-date">
                      {item.modified && new Date(item.modified).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="file-actions">
                    {item.type === 'file' && (
                      <button onClick={() => handleDownload(item.path)} title="Download">
                        <FiDownload />
                      </button>
                    )}
                    <button onClick={() => handleDelete(item.path)} title="Delete">
                      <FiTrash2 />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
