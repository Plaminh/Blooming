// @ts-nocheck
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function getAllFiles(dirPath: string, arrayOfFiles: string[] = []) {
  if (!fs.existsSync(dirPath)) return arrayOfFiles;
  
  const files = fs.readdirSync(dirPath);

  files.forEach(function (file) {
    const fullPath = path.join(dirPath, file);
    if (fs.statSync(fullPath).isDirectory()) {
      arrayOfFiles = getAllFiles(fullPath, arrayOfFiles);
    } else {
      if (file.endsWith('.ts') || file.endsWith('.svelte') || file.endsWith('.js')) {
        arrayOfFiles.push(fullPath);
      }
    }
  });

  return arrayOfFiles;
}

describe('Frontend Architecture Boundaries', () => {
  const rootDir = path.resolve(__dirname, '../lib');
  const allFiles = getAllFiles(rootDir).map(f => f.replace(/\\/g, '/'));

  it('shared should not import features', () => {
    const sharedFiles = allFiles.filter(f => f.includes('/lib/shared/'));
    const violations = [];
    
    for (const file of sharedFiles) {
      const content = fs.readFileSync(file, 'utf-8');
      if (content.includes('$lib/features/') || content.includes('../features/')) {
        violations.push(file);
      }
    }
    
    expect(violations).toEqual([]);
  });
  
  it('api should not import features', () => {
    const apiFiles = allFiles.filter(f => f.includes('/lib/api/'));
    const violations = [];
    
    for (const file of apiFiles) {
      const content = fs.readFileSync(file, 'utf-8');
      if (content.includes('$lib/features/') || content.includes('../features/')) {
        violations.push(file);
      }
    }
    
    expect(violations).toEqual([]);
  });

  it('features should not import other features directly', () => {
    const featureFiles = allFiles.filter(f => f.includes('/lib/features/'));
    const violations: string[] = [];
    
    // Explicit allowlist for justified legacy cases
    const allowlist = [
      {
        file: 'lib/features/garden/components/organisms/GardenPanel.test.ts',
        imports: ['$lib/features/garden-selection', '$lib/features/companion-widget']
      },
      {
        file: 'lib/features/garden/components/organisms/GardenPanel.svelte',
        imports: ['$lib/features/garden-selection', '$lib/features/companion-widget']
      },
      {
        file: 'lib/features/mr-bloom/components/atoms/ChatAvatar.svelte',
        imports: ['$lib/features/companion-widget']
      },
      {
        file: 'lib/features/mr-bloom/components/organisms/TimelineDraftPreview.svelte',
        imports: ['$lib/features/today']
      },
      {
        file: 'lib/features/today/components/organisms/CustomFocusDialog.svelte',
        imports: ['$lib/features/settings']
      },
      {
        file: 'lib/features/today/components/organisms/RightRail.svelte',
        imports: ['$lib/features/garden']
      }
    ];
    
    const importRegex = /import\s+(?:[^'"`]+\s+from\s+)?['"`]\s*([^`'"]+)\s*['"`]/g;
    
    for (const file of featureFiles) {
      const relativePath = file.substring(file.indexOf('/lib/features/'));
      const featureMatch = relativePath.match(/\/lib\/features\/([^\/]+)/);
      const featureName = featureMatch ? featureMatch[1] : null;
      
      const content = fs.readFileSync(file, 'utf-8');
      let match;
      while ((match = importRegex.exec(content)) !== null) {
        const importPath = match[1];
        
        let importedFeature = null;
        if (importPath.startsWith('$lib/features/')) {
          importedFeature = importPath.split('/')[2];
        } else if (importPath.includes('/features/')) {
           const parts = importPath.split('/features/');
           importedFeature = parts[1].split('/')[0];
        }
        
        if (importedFeature && importedFeature !== featureName) {
           const isAllowed = allowlist.some(a => 
              file.endsWith(a.file) && a.imports.some(i => importPath.startsWith(i))
           );
           
           if (!isAllowed) {
              violations.push(`${file.substring(file.indexOf('frontend/src'))} imports ${importPath}`);
           }
        }
      }
    }
    
    expect(violations).toEqual([]);
  });
  
  it('shared should not own domain API calls', () => {
    const sharedFiles = allFiles.filter(f => f.includes('/lib/shared/'));
    const violations = [];
    
    for (const file of sharedFiles) {
      const content = fs.readFileSync(file, 'utf-8');
      if (content.includes('fetch(') || content.includes('axios.')) {
        violations.push(file);
      }
    }
    
    expect(violations).toEqual([]);
  });
});
