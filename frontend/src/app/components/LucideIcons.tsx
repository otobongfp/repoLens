/**
 * RepoLens Frontend - Lucideicons Component
 * 
 * Copyright (C) 2024 RepoLens Contributors
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import React from 'react';

interface IconProps {
  className?: string;
  size?: number;
}

export const CodeIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-code-icon ${className}`}
  >
    <path d='m16 18 6-6-6-6' />
    <path d='m8 6-6 6 6 6' />
  </svg>
);

export const PuzzleIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-puzzle-icon ${className}`}
  >
    <path d='M15.39 4.39a1 1 0 0 0 1.68-.474 2.5 2.5 0 1 1 3.014 3.015 1 1 0 0 0-.474 1.68l1.683 1.682a2.414 2.414 0 0 1 0 3.414L19.61 15.39a1 1 0 0 1-1.68-.474 2.5 2.5 0 1 0-3.014 3.015 1 1 0 0 1 .474 1.68l-1.683 1.682a2.414 2.414 0 0 1-3.414 0L8.61 19.61a1 1 0 0 0-1.68.474 2.5 2.5 0 1 1-3.014-3.015 1 1 0 0 0 .474-1.68l-1.683-1.682a2.414 2.414 0 0 1 0-3.414L4.39 8.61a1 1 0 0 1 1.68.474 2.5 2.5 0 1 0 3.014-3.015 1 1 0 0 1-.474-1.68l1.683-1.682a2.414 2.414 0 0 1 3.414 0z' />
  </svg>
);

export const BrainIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-brain-icon ${className}`}
  >
    <path d='M12 18V5' />
    <path d='M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4' />
    <path d='M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5' />
    <path d='M17.997 5.125a4 4 0 0 1 2.526 5.77' />
    <path d='M18 18a4 4 0 0 0 2-7.464' />
    <path d='M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517' />
    <path d='M6 18a4 4 0 0 1-2-7.464' />
    <path d='M6.003 5.125a4 4 0 0 0-2.526 5.77' />
  </svg>
);

export const BotIcon: React.FC<IconProps> = ({ className = '', size = 24 }) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-bot-icon ${className}`}
  >
    <path d='M12 8V4H8' />
    <rect width='16' height='12' x='4' y='8' rx='2' />
    <path d='M2 14h2' />
    <path d='M20 14h2' />
    <path d='M15 13v2' />
    <path d='M9 13v2' />
  </svg>
);

export const SettingsIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-settings-icon ${className}`}
  >
    <path d='M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z' />
    <circle cx='12' cy='12' r='3' />
  </svg>
);

export const MenuIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-menu-icon ${className}`}
  >
    <line x1='4' x2='20' y1='12' y2='12' />
    <line x1='4' x2='20' y1='6' y2='6' />
    <line x1='4' x2='20' y1='18' y2='18' />
  </svg>
);

export const XIcon: React.FC<IconProps> = ({ className = '', size = 24 }) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-x-icon ${className}`}
  >
    <path d='M18 6L6 18' />
    <path d='M6 6l12 12' />
  </svg>
);

export const ChevronDownIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-chevron-down-icon ${className}`}
  >
    <path d='m6 9 6 6 6-6' />
  </svg>
);

export const ChevronUpIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-chevron-up-icon ${className}`}
  >
    <path d='m18 15-6-6-6 6' />
  </svg>
);

export const DatabaseIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-database-icon ${className}`}
  >
    <ellipse cx='12' cy='5' rx='9' ry='3' />
    <path d='M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5' />
    <path d='M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3' />
  </svg>
);

export const FolderIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-folder-icon ${className}`}
  >
    <path d='M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z' />
  </svg>
);

export const PlusIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-plus-icon ${className}`}
  >
    <path d='M5 12h14' />
    <path d='M12 5v14' />
  </svg>
);

export const GithubIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-github-icon ${className}`}
  >
    <path d='M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4' />
    <path d='M9 18c-4.51 2-5-2-7-2' />
  </svg>
);

export const CloudIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-cloud-icon ${className}`}
  >
    <path d='M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z' />
  </svg>
);

export const HardDriveIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-hard-drive-icon ${className}`}
  >
    <line x1='22' x2='2' y1='12' y2='12' />
    <path d='M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z' />
    <line x1='6' x2='6.01' y1='16' y2='16' />
    <line x1='10' x2='10.01' y1='16' y2='16' />
  </svg>
);

export const MoreVerticalIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-more-vertical-icon ${className}`}
  >
    <circle cx='12' cy='12' r='1' />
    <circle cx='12' cy='5' r='1' />
    <circle cx='12' cy='19' r='1' />
  </svg>
);

export const TrashIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-trash-icon ${className}`}
  >
    <path d='M3 6h18' />
    <path d='M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6' />
    <path d='M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2' />
  </svg>
);

export const EditIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-edit-icon ${className}`}
  >
    <path d='M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7' />
    <path d='M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z' />
  </svg>
);

export const PlayIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-play-icon ${className}`}
  >
    <polygon points='5,3 19,12 5,21' />
  </svg>
);

export const ClockIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-clock-icon ${className}`}
  >
    <circle cx='12' cy='12' r='10' />
    <polyline points='12,6 12,12 16,14' />
  </svg>
);

export const CheckCircleIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-check-circle-icon ${className}`}
  >
    <path d='M22 11.08V12a10 10 0 1 1-5.93-9.14' />
    <polyline points='22,4 12,14.01 9,11.01' />
  </svg>
);

export const XCircleIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-x-circle-icon ${className}`}
  >
    <circle cx='12' cy='12' r='10' />
    <path d='m15 9-6 6' />
    <path d='m9 9 6 6' />
  </svg>
);

export const AlertCircleIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-alert-circle-icon ${className}`}
  >
    <circle cx='12' cy='12' r='10' />
    <line x1='12' x2='12' y1='8' y2='12' />
    <line x1='12' x2='12.01' y1='16' y2='16' />
  </svg>
);

export const BarChartIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-bar-chart-icon ${className}`}
  >
    <line x1='12' x2='12' y1='20' y2='10' />
    <line x1='18' x2='18' y1='20' y2='4' />
    <line x1='6' x2='6' y1='20' y2='16' />
  </svg>
);

export const CheckIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-check-icon ${className}`}
  >
    <polyline points='20,6 9,17 4,12' />
  </svg>
);

export const KeyIcon: React.FC<IconProps> = ({ className = '', size = 24 }) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-key-icon ${className}`}
  >
    <circle cx='7.5' cy='15.5' r='5.5' />
    <path d='m21 2-9.6 9.6' />
    <path d='m15.5 7.5 3 3L22 7l-3-3' />
  </svg>
);

export const RefreshIcon: React.FC<IconProps> = ({
  className = '',
  size = 24,
}) => (
  <svg
    xmlns='http://www.w3.org/2000/svg'
    width={size}
    height={size}
    viewBox='0 0 24 24'
    fill='none'
    stroke='currentColor'
    strokeWidth='2'
    strokeLinecap='round'
    strokeLinejoin='round'
    className={`lucide lucide-refresh-icon ${className}`}
  >
    <path d='M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8' />
    <path d='M21 3v5h-5' />
    <path d='M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16' />
    <path d='M3 21v-5h5' />
  </svg>
);
