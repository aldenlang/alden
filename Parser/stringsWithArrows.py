def stringsWithArrows(text, pos_start, pos_end):
    result = ''
    error = ''
    # Calculate indices
    index_start = max(text.rfind('\n', 0, pos_start.index), 0)
    index_end = text.find('\n', index_start + 1)
    if index_end < 0: index_end = len(text)
    
    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        # Calculate line columnumns
        line = text[index_start:index_end]
        column_start = pos_start.column if i == 0 else 0
        column_end = pos_end.column if i == line_count - 1 else len(line) - 1

        
        error += line + '\n'
        error += ' ' * column_start + '^' * (column_end - column_start + 1)
        error_at = error.find('^')
        error_at_text = error[:error_at]
        print(pos_start)
        # Append to result
        result = error_at_text
        result += '\n' + '^' * len(error_at_text.rstrip()) + '\n'
        # Re-calculate indices
        index_start = index_end
        index_end = text.find('\n', index_start + 1)
        if index_end < 0: index_end = len(text)
        
    return result.replace('\t', '')


