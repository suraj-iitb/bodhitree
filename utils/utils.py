import os


def get_course_folder(course):
    course_id = course.id
    course_code = course.code.replace(" ", "_")
    course_title = course.title.replace(" ", "_")
    if course_code:
        return "{}.{}:{}".format(course_id, course_code, course_title)
    return "{}.{}".format(course_id, course_title)


def get_assignment_folder(assignment, assignment_type):
    assignment_id = assignment.id
    assignment_name = assignment.name.replace(" ", "_")
    assignment_folder = "{}.{}".format(assignment_id, assignment_name)
    if assignment_type == "programming":
        return os.path.join("ProgrammingAssignment", assignment_folder)
    elif assignment_type == "subjective":
        return os.path.join("SubjectiveAssignment", assignment_folder)


def get_assignment_file_upload_path(assignment, assignment_type, sub_folder, filename):
    course_folder = get_course_folder(assignment.course)
    assignment_folder = get_assignment_folder(assignment, assignment_type)
    return os.path.join(course_folder, assignment_folder, sub_folder, filename)
