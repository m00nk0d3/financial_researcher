"""Log parser for extracting structured events from CrewAI output."""
import re
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum


class EventType(Enum):
    """Types of events that can be extracted from logs."""
    AGENT_START = "agent_start"
    AGENT_CHANGE = "agent_change"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TOOL_USE = "tool_use"
    THINKING = "thinking"
    ACTION = "action"
    OBSERVATION = "observation"
    LOG = "log"


class LogParser:
    """Parses CrewAI output to extract structured events."""
    
    # Patterns for different event types
    AGENT_PATTERNS = [
        r'# Agent:\s*(.+?)(?:\n|$)',
        r'Agent:\s*(.+?)(?:\n|$)',
        r'Working Agent:\s*(.+?)(?:\n|$)',
    ]
    
    TASK_PATTERNS = [
        r'# Task:\s*(.+?)(?:\n|$)',
        r'## Task:\s*(.+?)(?:\n|$)',
        r'Beginning:\s*(.+?)(?:\n|$)',
    ]
    
    TOOL_PATTERNS = [
        r'Using tool:\s*(.+?)(?:\n|$)',
        r'Tool:\s*(.+?)(?:\n|$)',
        r'Action:\s*(.+?)(?:\n|$)',
    ]
    
    THINKING_PATTERNS = [
        r'Thought:\s*(.+?)(?:\n|$)',
        r'Reasoning:\s*(.+?)(?:\n|$)',
        r'I need to\s*(.+?)(?:\n|$)',
        r'I will\s*(.+?)(?:\n|$)',
    ]
    
    OBSERVATION_PATTERNS = [
        r'Observation:\s*(.+?)(?:\n|$)',
        r'Result:\s*(.+?)(?:\n|$)',
    ]
    
    def __init__(self):
        self.current_agent = None
        self.current_task = None
        self.last_event_type = None
    
    def parse_line(self, line: str) -> List[Dict]:
        """
        Parse a single log line and return structured events.
        
        Returns a list because one line might generate multiple events.
        """
        if not line or not line.strip():
            return []
        
        events = []
        line = line.strip()
        
        # Check for agent
        agent_event = self._parse_agent(line)
        if agent_event:
            events.append(agent_event)
        
        # Check for task
        task_event = self._parse_task(line)
        if task_event:
            events.append(task_event)
        
        # Check for tool usage
        tool_event = self._parse_tool(line)
        if tool_event:
            events.append(tool_event)
        
        # Check for thinking
        thinking_event = self._parse_thinking(line)
        if thinking_event:
            events.append(thinking_event)
        
        # Check for observation
        observation_event = self._parse_observation(line)
        if observation_event:
            events.append(observation_event)
        
        # If no specific event, treat as regular log
        if not events:
            events.append(self._create_log_event(line))
        
        return events
    
    def _parse_agent(self, line: str) -> Optional[Dict]:
        """Extract agent information from line."""
        for pattern in self.AGENT_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                agent_name = match.group(1).strip()
                
                # Determine agent role
                role = self._determine_agent_role(agent_name)
                
                # Check if this is a change or start
                event_type = EventType.AGENT_START if not self.current_agent else EventType.AGENT_CHANGE
                self.current_agent = agent_name
                
                return {
                    'type': event_type.value,
                    'timestamp': self._get_timestamp(),
                    'data': {
                        'agent': agent_name,
                        'role': role,
                        'raw_line': line
                    }
                }
        return None
    
    def _parse_task(self, line: str) -> Optional[Dict]:
        """Extract task information from line."""
        for pattern in self.TASK_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                task_name = match.group(1).strip()
                self.current_task = task_name
                
                return {
                    'type': EventType.TASK_START.value,
                    'timestamp': self._get_timestamp(),
                    'data': {
                        'task': task_name,
                        'agent': self.current_agent,
                        'raw_line': line
                    }
                }
        
        # Check for task completion indicators
        if re.search(r'task output|completed|finished', line, re.IGNORECASE):
            return {
                'type': EventType.TASK_COMPLETE.value,
                'timestamp': self._get_timestamp(),
                'data': {
                    'task': self.current_task,
                    'agent': self.current_agent,
                    'raw_line': line
                }
            }
        
        return None
    
    def _parse_tool(self, line: str) -> Optional[Dict]:
        """Extract tool usage information from line."""
        for pattern in self.TOOL_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                tool_info = match.group(1).strip()
                
                # Try to extract tool name and action
                tool_name = tool_info
                action = None
                
                # Common tool names
                if 'serper' in tool_info.lower():
                    tool_name = 'SerperDevTool'
                    action = 'Search'
                elif 'search' in tool_info.lower():
                    tool_name = 'Search'
                    action = 'Query'
                
                return {
                    'type': EventType.TOOL_USE.value,
                    'timestamp': self._get_timestamp(),
                    'data': {
                        'tool': tool_name,
                        'action': action,
                        'agent': self.current_agent,
                        'raw_line': line
                    }
                }
        return None
    
    def _parse_thinking(self, line: str) -> Optional[Dict]:
        """Extract thinking/reasoning information from line."""
        for pattern in self.THINKING_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                
                return {
                    'type': EventType.THINKING.value,
                    'timestamp': self._get_timestamp(),
                    'data': {
                        'thought': thought,
                        'agent': self.current_agent,
                        'raw_line': line
                    }
                }
        return None
    
    def _parse_observation(self, line: str) -> Optional[Dict]:
        """Extract observation/result information from line."""
        for pattern in self.OBSERVATION_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                observation = match.group(1).strip()
                
                return {
                    'type': EventType.OBSERVATION.value,
                    'timestamp': self._get_timestamp(),
                    'data': {
                        'observation': observation,
                        'agent': self.current_agent,
                        'raw_line': line
                    }
                }
        return None
    
    def _create_log_event(self, line: str) -> Dict:
        """Create a generic log event."""
        return {
            'type': EventType.LOG.value,
            'timestamp': self._get_timestamp(),
            'data': {
                'message': line,
                'agent': self.current_agent,
                'task': self.current_task
            }
        }
    
    def _determine_agent_role(self, agent_name: str) -> str:
        """Determine the role identifier from agent name."""
        agent_lower = agent_name.lower()
        
        if 'research' in agent_lower:
            return 'researcher'
        elif 'analyst' in agent_lower or 'analysis' in agent_lower:
            return 'analyst'
        else:
            return 'unknown'
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp."""
        return datetime.now().strftime('%H:%M:%S')
    
    def reset(self):
        """Reset parser state."""
        self.current_agent = None
        self.current_task = None
        self.last_event_type = None
