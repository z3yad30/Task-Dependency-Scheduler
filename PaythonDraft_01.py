import networkx as nx
import matplotlib.pyplot as plt
from networkx.classes.graph import Graph


class TaskScheduler:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.task_details = {}

    def add_task(self, task, dependencies=None, priority=None, deadline=None, description=None):
        if task in self.graph:
            raise ValueError(f"Task '{task}' already exists.")
        self.graph.add_node(task)
        self.task_details[task] = {
            "dependencies": dependencies,
            "priority": priority,
            "deadline": deadline,
            "description": description
        }
        if dependencies:
            for dep in dependencies:
                if dep not in self.graph:
                    raise ValueError(f"Dependency '{dep}' does not exist.")
                self.graph.add_edge(dep, task)

    def edit_task(self, old_task_name):  # make it edit the whole task and handle it in the main
        print(f"Old task details are: {self.task_details[old_task_name]}")
        tasks_depends_on = []  # Collect every task that depends on the old task name
        for i in self.graph:
            if old_task_name in self.task_details[i]['dependencies']:
                tasks_depends_on.append(i)

        old_task_dependencies = [self.task_details[old_task_name]['dependencies']]

        new_task_name = input(f"Enter the new task name: ").strip()
        if new_task_name in self.graph and new_task_name != old_task_name:
            raise ValueError(f"Task '{new_task_name}' already exists.")

        new_priority = ""
        while True:
            new_priority = input(f"Enter a new priority for task {new_task_name} [0, 10]: ")
            if new_priority.isdigit() and 0 <= int(new_priority) <= 10:
                new_priority = int(new_priority)
                break
            else:
                print("Error: Priority must be a number [0, 10]. Please enter a valid number.")

        new_deadline = {
            'year': '----',
            'month': '--',
            'day': '--',
        }
        answer = input(f"Does {new_task_name} have a deadline? [yes, no]: ")
        if answer == "yes":
            while True:
                year = input(f"{new_task_name} [year] deadline is: ").strip()
                month = input(f"{new_task_name} [month] deadline is: ").strip()
                day = input(f"{new_task_name} [day] deadline is: ").strip()
                if not (year.isdigit() and month.isdigit() and day.isdigit()):
                    print("Error, renter a valid deadline")
                elif not ((int(year) > 2024 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31) or (int(year) == 2024 and 12 <= int(month) <= 12 and 29 <= int(day) <= 31)):
                    print(f"Error, current date is 29/12/2024 don't enter deadline before this one, enter a valid deadline")
                elif (year.isdigit() and month.isdigit() and day.isdigit()):
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    new_deadline['year'] = year
                    new_deadline['month'] = month
                    new_deadline['day'] = day
                    break
        elif answer == "no":
            print(f"The deadline will remain blank for the task {new_task_name}")

        new_description = input("Enter task description: ").strip()
        new_dependencies = input(
            f"Enter the dependencies for task {new_task_name} (comma-separated, leave blank if none): ").strip()
        new_dependencies = [dep.strip() for dep in new_dependencies.split(",")] if new_dependencies else []
        for i in new_dependencies:
            if i not in self.graph:
                raise ValueError(f"Dependency '{i}' does not exist.")
            # self.graph.add_edge(i, new_task_name)

        # Add the new task
        self.add_task(new_task_name, new_dependencies, new_priority, new_deadline, new_description)

        # Edit each task that depends on the old task
        for task in tasks_depends_on:
            self.graph.add_edge(new_task_name, task)

        # Delete the old task from the graph
        # self.delete_task(old_task_name)
        self.graph.remove_node(old_task_name)
        del self.task_details[old_task_name]

    def delete_task(self, task_name):
        if task_name not in self.graph:
            raise ValueError(f"Task '{task_name}' does not exist.")

        # Get predecessors (dependencies) and successors (dependent tasks) of the target task
        predecessors = list(self.graph.predecessors(task_name))
        successors = list(self.graph.successors(task_name))

        # Reassign dependencies: Make each successor of the target task depend on its predecessors
        for successor in successors:
            for predecessor in predecessors:
                self.graph.add_edge(predecessor, successor)

        # Remove the task from the graph and its details
        self.graph.remove_node(task_name)
        del self.task_details[task_name]

        print(f"Task '{task_name}' has been successfully deleted. Its dependencies have been reassigned.")

    def edit_dependencies(self, task, new_dependencies):
        if task not in self.graph:
            raise ValueError(f"Task '{task}' does not exist.")
        for predecessor in list(self.graph.predecessors(task)):
            self.graph.remove_edge(predecessor, task)
        for dep in new_dependencies:
            if dep not in self.graph:
                raise ValueError(f"Dependency '{dep}' does not exist.")
            self.graph.add_edge(dep, task)

    def detect_cycle(self):
        def dfs(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    has_cycle, cycle_path = dfs(neighbor, visited, rec_stack)
                    if has_cycle:
                        cycle_path.append(node)
                        return True, cycle_path
                elif neighbor in rec_stack:
                    return True, [neighbor, node]

            rec_stack.remove(node)
            return False, []

        visited = set()
        rec_stack = set()

        for node in self.graph:
            if node not in visited:
                has_cycle, cycle_path = dfs(node, visited, rec_stack)
                if has_cycle:
                    cycle_path.reverse()
                    return True, cycle_path

        return False, []

    def topological_sort(self):
        detected, cycle = self.detect_cycle()
        if detected:
            print("There is a cycle, can't perform topological sort due to the cycle.")
            return None
        visited = set()
        stack = []

        def dfs(node):
            visited.add(node)
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
            stack.append(node)

        for node in self.graph.nodes:
            if node not in visited:
                dfs(node)

        return stack[::-1]

    def get_priority(self, task):
        return self.task_details[task]["priority"]

    def STBP(self):
        sorted_tasks = sorted(self.graph.nodes, key=self.get_priority, reverse=True)
        return sorted_tasks

    def visualize(self):
        if self.graph.number_of_nodes() == 0:
            raise ValueError("Cannot visualize an empty graph.")
        nx.draw(self.graph, with_labels=True, node_color='skyblue', font_weight='bold', node_size=2000, font_size=10)
        plt.show()

    def sort_by_deadline(self):
        def get_deadline_key(task):
            deadline = self.task_details[task]["deadline"]
            INT_MAX = 2**31 - 1
            year = int(deadline.get('year')) if str(deadline.get('year')).isdigit() else INT_MAX
            month = int(deadline.get('month')) if str(deadline.get('month')).isdigit() else INT_MAX
            day = int(deadline.get('day')) if str(deadline.get('day')).isdigit() else INT_MAX
            return (year, month, day)

        sorted_tasks = sorted(self.graph.nodes, key=get_deadline_key)
        return sorted_tasks


    def ETN(self, old_task_name, new_task_name):
        if old_task_name not in self.graph:
            raise ValueError(f"Task '{old_task_name}' does not exist.")
        if new_task_name.strip() == "":
            raise ValueError("New task name cannot be empty.")
        if new_task_name in self.graph:
            raise ValueError(f"Task '{new_task_name}' already exists.")
        self.graph = nx.relabel_nodes(self.graph, {old_task_name: new_task_name})
        self.task_details[new_task_name] = self.task_details.pop(old_task_name)
        print(f"Task '{old_task_name}' has been renamed to '{new_task_name}'.")

    def edit_priority(self, task):
        if task not in self.graph:
            raise ValueError(f"Task '{task}' does not exist.")

        while True:
            new_priority = input(f"Enter a new priority for task '{task}' [0, 10]: ").strip()
            if new_priority.isdigit() and 0 <= int(new_priority) <= 10:
                self.task_details[task]["priority"] = int(new_priority)
                print(f"Priority of task '{task}' updated to {new_priority}.")
                break
            else:
                print("Error: Priority must be a number between 0 and 10. Please enter a valid value.")

    def edit_description(self, task):
        if task not in self.graph:
            raise ValueError(f"Task '{task}' does not exist.")

        print(f"Current description for task '{task}': {self.task_details[task]['description']}")
        new_description = input("Enter a new description for the task: ").strip()
        self.task_details[task]["description"] = new_description
        print(f"Description for task '{task}' has been updated to: {new_description}")

    def edit_deadline(self, task):
        if task not in self.graph:
            raise ValueError(f"Task '{task}' does not exist.")

        print(f"Current deadline for task '{task}': {self.task_details[task]['deadline']}")


        answer = input(f"Does the task '{task}' have a new deadline? [yes, remove, cancle]: ").strip().lower()

        if answer == "yes":
            new_deadline = {
                'year': '----',
                'month': '--',
                'day': '--',
            }
            while True:
                year = input(f"{task} [year] deadline is: ").strip()
                month = input(f"{task} [month] deadline is: ").strip()
                day = input(f"{task} [day] deadline is: ").strip()
                if not (year.isdigit() and month.isdigit() and day.isdigit()):
                    print("Error, renter a valid deadline")
                elif not ((int(year) > 2024 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31) or (int(year) == 2024 and 12 <= int(month) <= 12 and 29 <= int(day) <= 31)):
                    print(f"Error, current date is 29/12/2024 don't enter deadline before this one, enter a valid deadline")
                elif (year.isdigit() and month.isdigit() and day.isdigit()):
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    new_deadline['year'] = year
                    new_deadline['month'] = month
                    new_deadline['day'] = day
                    break

            self.task_details[task]["deadline"] = new_deadline
            print(f"Deadline for task '{task}' has been updated to: {new_deadline}")

        elif answer == "remove":

            self.task_details[task]["deadline"] = {
                'year': '----',
                'month': '--',
                'day': '--',
            }
            print(f"The deadline for task '{task}' has been removed and is now empty.")

        elif answer == "cancle":
            print(f"The deadline for task '{task}' will remain unchanged.")


def main():
    scheduler = TaskScheduler()

    print("Welcome to the Task Scheduler!")
    while True:
        print("\nMenu:")
        print("1. Add a task")
        print("2. Edit task dependencies")
        print("3. Detect cycles")
        print("4. Perform topological sort")
        print("5. Visualize task graph")
        print("6. Sort tasks by priority")
        print("7. Edit task")
        print("8. Sort tasks by deadline")
        print("9. delet task")
        print("10. edit task name")
        print("11. Edit task priority")
        print("12. Edit task description")
        print("13. Edit task deadline")
        print("14. Exit")

        choice = input("Enter your choice (1-14): ").strip()

        try:
            if choice == "1":
                task = input("Enter the task name: ").strip()
                if task in scheduler.graph:
                    print(f"Error: Task '{task}' already exists. Please try again.")
                    continue
                while True:
                    dependencies = input("Enter dependencies (comma-separated, leave blank if none): ").strip()
                    dependencies = [dep.strip() for dep in dependencies.split(",")] if dependencies else []

                    while True:
                        priority = input("Enter priority [0 , 10] (higher number is higher priority): ").strip()
                        if priority.isdigit() and 0 <= int(priority) <= 10:
                            priority = int(priority)
                            break
                        else:
                            print("Error: Priority must be a number [0 , 10]. Please enter a valid number.")
                    deadline = {
                        'year': '----',
                        'month': '--',
                        'day': '--',
                    }
                    answer = input(f"does {task} have deadline? [yes , no] : ")
                    if answer == "yes":
                        while True:
                            year = input(f"{task} [ year ] dead line is : ").strip()
                            month = input(f"{task} [ month ] dead line is : ").strip()
                            day = input(f"{task} [ day ] dead line is : ").strip()
                            if not (year.isdigit() and month.isdigit() and day.isdigit()):
                                print("Error, renter a valid deadline")
                            elif not ((int(year) > 2024 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31) or (int(year) == 2024 and 12 <= int(month) <= 12 and 29 <= int(day) <= 31)):
                                print(f"Error, current date is 29/12/2024 don't enter deadline before this one, enter a valid deadline")
                            elif (year.isdigit() and month.isdigit() and day.isdigit()):
                                year = int(year)
                                month = int(month)
                                day = int(day)
                                deadline['year'] = year
                                deadline['month'] = month
                                deadline['day'] = day
                                break
                        # deadline = input("Enter deadline (YYYY-MM-DD): ").strip()
                    if answer == "no":
                        print(f"will, the deadline will be blank value for the task {task}")
                    description = input("Enter task description: ").strip()

                    try:
                        scheduler.add_task(task, dependencies, priority, deadline, description)
                        print(
                            f"Task '{task}' added successfully with dependencies: {dependencies}, priority: {priority}, deadline: {deadline}, description: {description}")
                        break
                    except ValueError as e:
                        print(f"Error: {e}. Please enter dependencies again.")

            elif choice == "2":
                task = input("Enter the task name to edit dependencies: ").strip()
                new_dependencies = input("Enter new dependencies (comma-separated, leave blank if none): ").strip()
                new_dependencies = [dep.strip() for dep in new_dependencies.split(",")] if new_dependencies else []
                try:
                    scheduler.edit_dependencies(task, new_dependencies)
                    print(f"Dependencies for task '{task}' updated to: {new_dependencies}")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "3":
                has_cycle, cycle_details = scheduler.detect_cycle()
                if has_cycle:
                    print("Cycle detected:", cycle_details)
                else:
                    print("No cycle detected.")

            elif choice == "4":
                sorted_tasks = scheduler.topological_sort()
                if sorted_tasks:
                    print("Topological order of tasks:", sorted_tasks)
                else:
                    print("Cannot perform topological sort due to a cycle.")

            elif choice == "5":
                print("Visualizing the task graph...")
                scheduler.visualize()

            elif choice == "6":
                sorted_tasks = scheduler.STBP()
                if sorted_tasks:
                    print("Tasks sorted by priority:", end=" ")
                    for i in sorted_tasks:
                        print(f"{i}[{scheduler.get_priority(i)}]", end=" ")
                else:
                    print("No tasks to sort.")

            elif choice == "7":
                old_task_name = input("Enter the task name to edit: ").strip()
                while old_task_name not in scheduler.graph:
                    old_task_name = input(f"{old_task_name} not in the current graf, renter an exist task please: ")

                try:
                    scheduler.edit_task(old_task_name)
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "8":
                sorted_tasks = scheduler.sort_by_deadline()
                if sorted_tasks:
                    print("Tasks sorted by deadline:", end=" ")
                    for task in sorted_tasks:
                        deadline = scheduler.task_details[task]["deadline"]
                        print(f"{task}[{deadline}]", end=" ")
                    print()
                else:
                    print("No tasks to sort by deadline.")
            elif choice == "9":
                task = input("Enter the task name: ").strip()
                scheduler.delete_task(task)
            elif choice == "10":
                old_task_name = input("Enter the task name to edit: ").strip()
                new_task_name = input("Enter new task name: ").strip()
                try:
                    scheduler.ETN(old_task_name, new_task_name)
                except ValueError as e:
                    print(f"Error: {e}")
            elif choice == "11":
                task = input("Enter the task name to edit its priority: ").strip()
                try:
                    scheduler.edit_priority(task)
                except ValueError as e:
                    print(f"Error: {e}")
            elif choice == "12":
                task = input("Enter the task name to edit its description: ").strip()
                try:
                    scheduler.edit_description(task)
                except ValueError as e:
                    print(f"Error: {e}")
            elif choice == "13":
                task = input("Enter the task name to edit its deadline: ").strip()
                try:
                    scheduler.edit_deadline(task)  # Call the edit_deadline function
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "14":
                print("Exiting. Goodbye!")
                break

            else:
                print("Invalid choice. Please enter a number between 1 and 8.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
