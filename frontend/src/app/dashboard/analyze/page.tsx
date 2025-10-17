'use client';

export const runtime = 'edge';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useRepolensApi, Project } from '../../utils/api';
import MainTabs from '../../components/MainTabs';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useGraphData } from '../../context/GraphDataProvider';
import {
  FolderIcon,
  GithubIcon,
  HardDriveIcon,
  PlayIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  AlertCircleIcon,
} from '../../components/LucideIcons';
import toast from 'react-hot-toast';

export default function AnalyzePage() {
  const router = useRouter();
  const { getProjects, analyzeProject } = useRepolensApi();
  const { graph, isLoading, error } = useGraphData();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [analyzingProject, setAnalyzingProject] = useState<string | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoadingProjects(true);
      const response = await getProjects();
      setProjects(response.projects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      toast.error('Failed to load projects');
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleAnalyzeProject = async (project: Project) => {
    try {
      setAnalyzingProject(project.project_id);
      setSelectedProject(project);

      await analyzeProject(project.project_id, 'full', false);

      toast.success(`Analysis started for ${project.name}`);

      // Navigate to show the analysis results
      // The graph data will be loaded automatically
    } catch (error) {
      console.error('Failed to start analysis:', error);
      toast.error('Failed to start analysis');
    } finally {
      setAnalyzingProject(null);
    }
  };

  const getProjectIcon = (project: Project) => {
    switch (project.source_config.type) {
      case 'github':
        return <GithubIcon className='h-5 w-5' />;
      case 'local':
      default:
        return <HardDriveIcon className='h-5 w-5' />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircleIcon className='h-4 w-4 text-green-500' />;
      case 'analyzing':
        return <ClockIcon className='h-4 w-4 animate-spin text-blue-500' />;
      case 'completed':
        return <CheckCircleIcon className='h-4 w-4 text-green-500' />;
      case 'error':
        return <XCircleIcon className='h-4 w-4 text-red-500' />;
      case 'cloning':
        return <ClockIcon className='h-4 w-4 animate-spin text-yellow-500' />;
      default:
        return <AlertCircleIcon className='h-4 w-4 text-gray-500' />;
    }
  };

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'Unknown';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loadingProjects) {
    return (
      <div className='flex min-h-[60vh] flex-col items-center justify-center'>
        <LoadingSpinner />
        <p className='text-muted-foreground mt-4'>Loading projects...</p>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className='flex min-h-[60vh] flex-col items-center justify-center'>
        <div className='text-center'>
          <FolderIcon className='mx-auto mb-4 h-16 w-16 text-gray-400' />
          <h1 className='text-foreground mb-2 font-serif text-3xl font-bold tracking-tighter md:text-4xl'>
            No Projects Found
          </h1>
          <p className='text-muted-foreground mb-6 max-w-xl text-sm md:text-base'>
            Create a project first to start analyzing your code
          </p>
          <button
            onClick={() => router.push('/dashboard/projects')}
            className='bg-primary hover:bg-primary/80 text-primary-foreground rounded-lg px-6 py-3 font-semibold transition'
          >
            Go to Projects
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className='flex min-h-[60vh] flex-col'>
      {/* Header */}
      <div className='mb-8 text-center'>
        <h1 className='text-foreground mb-2 font-serif text-3xl font-bold tracking-tighter md:text-4xl'>
          Analyze Project
        </h1>
        <p className='text-muted-foreground max-w-xl text-sm md:text-base'>
          Select a project to analyze and explore its structure
        </p>
      </div>

      {/* Project Selection */}
      {!selectedProject && (
        <div className='mb-8 w-full max-w-4xl'>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            {projects.map((project) => (
              <div
                key={project.project_id}
                className='rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md transition hover:border-white/20'
              >
                <div className='mb-4 flex items-start gap-3'>
                  {getProjectIcon(project)}
                  <div className='min-w-0 flex-1'>
                    <h3 className='text-foreground mb-1 truncate font-semibold'>
                      {project.name}
                    </h3>
                    <p className='text-muted-foreground truncate text-sm'>
                      {project.source_config.type === 'github'
                        ? project.source_config.github_url
                        : project.source_config.local_path}
                    </p>
                  </div>
                  {getStatusIcon(project.status)}
                </div>

                {project.description && (
                  <p className='text-muted-foreground mb-4 text-sm'>
                    {project.description}
                  </p>
                )}

                <div className='mb-4 space-y-2 text-xs text-gray-400'>
                  <div className='flex justify-between'>
                    <span>Files: {project.file_count || 'Unknown'}</span>
                    <span>Size: {formatBytes(project.size_bytes)}</span>
                  </div>
                  <div className='flex justify-between'>
                    <span>Analyses: {project.analysis_count}</span>
                    <span>Created: {formatDate(project.created_at)}</span>
                  </div>
                  {project.last_analyzed && (
                    <div className='text-center'>
                      <span>
                        Last analyzed: {formatDate(project.last_analyzed)}
                      </span>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleAnalyzeProject(project)}
                  disabled={
                    project.status === 'analyzing' ||
                    project.status === 'cloning'
                  }
                  className='bg-primary hover:bg-primary/80 text-primary-foreground w-full rounded-lg px-4 py-2 font-semibold transition disabled:opacity-50'
                >
                  {project.status === 'analyzing' ||
                  project.status === 'cloning' ? (
                    <div className='flex items-center justify-center gap-2'>
                      <ClockIcon className='h-4 w-4 animate-spin' />
                      {project.status === 'analyzing'
                        ? 'Analyzing...'
                        : 'Cloning...'}
                    </div>
                  ) : (
                    <div className='flex items-center justify-center gap-2'>
                      <PlayIcon className='h-4 w-4' />
                      Analyze Project
                    </div>
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Progress */}
      {selectedProject &&
        (selectedProject.status === 'analyzing' ||
          selectedProject.status === 'cloning') && (
          <div className='mb-8 w-full max-w-2xl'>
            <div className='rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
              <div className='text-center'>
                <div className='mb-4'>
                  {selectedProject.status === 'analyzing' ? (
                    <ClockIcon className='mx-auto h-12 w-12 animate-spin text-blue-500' />
                  ) : (
                    <ClockIcon className='mx-auto h-12 w-12 animate-spin text-yellow-500' />
                  )}
                </div>
                <h3 className='text-foreground mb-2 text-lg font-semibold'>
                  {selectedProject.status === 'analyzing'
                    ? 'Analyzing Project'
                    : 'Preparing Project'}
                </h3>
                <p className='text-muted-foreground mb-4 text-sm'>
                  {selectedProject.status === 'analyzing'
                    ? `Analyzing ${selectedProject.name} and creating AST relationships...`
                    : `Cloning ${selectedProject.name} from ${selectedProject.source_config.type === 'github' ? 'GitHub' : 'local path'}...`}
                </p>
                <div className='bg-background rounded-lg p-4'>
                  <div className='text-muted-foreground text-xs'>
                    <div className='mb-2'>Project: {selectedProject.name}</div>
                    <div className='mb-2'>
                      Source: {selectedProject.source_config.type}
                    </div>
                    <div>Status: {selectedProject.status}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      {/* Loading State for Analysis */}
      {isLoading && (
        <div className='mb-8'>
          <LoadingSpinner />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className='mb-8 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-center'>
          <p className='text-red-300'>{error}</p>
        </div>
      )}

      {/* Analysis Results */}
      {graph && selectedProject && (
        <div className='w-full max-w-6xl'>
          <div className='mb-4 rounded-lg border border-white/10 bg-white/5 p-4'>
            <div className='flex items-center gap-3'>
              {getProjectIcon(selectedProject)}
              <div>
                <h3 className='text-foreground font-semibold'>
                  {selectedProject.name}
                </h3>
                <p className='text-muted-foreground text-sm'>
                  Analysis completed successfully
                </p>
              </div>
            </div>
          </div>
          <div className='rounded-2xl border border-white/10 bg-white/5 p-4 shadow-xl backdrop-blur-md sm:p-6'>
            <MainTabs />
          </div>
        </div>
      )}
    </div>
  );
}
