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
